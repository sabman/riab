import unittest
import numpy
import os
import impact

from impact.storage.raster import Raster
from impact.storage.vector import Vector
from impact.storage.projection import Projection
from impact.storage.io import read_layer
from impact.storage.io import write_point_data
from impact.storage.io import write_raster_data
from impact.storage.utilities import unique_filename
from impact.storage.io import get_bounding_box
from impact.tests.utilities import same_API
from impact.storage.utilities import DEFAULT_PROJECTION
from impact.tests.utilities import TESTDATA


# Auxiliary function for raster test
def linear_function(x, y):
    """Auxiliary function for use with raster test
    """

    return x + y / 2.


class Test_IO(unittest.TestCase):
    """Tests for reading and writing of raster and vector data
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_instantiation_of_empty_layers(self):
        """Vector and Raster objects can be instantiated with None
        """

        v = Vector(None)
        assert v.get_name().startswith('Vector')

        r = Raster(None)
        assert r.get_name().startswith('Raster')

    def test_reading_and_writing_of_vector_data(self):
        """Vector data can be read and written correctly
        """

        # First test that some error conditions are caught
        filename = unique_filename(suffix='nshoe66u')
        try:
            read_layer(filename)
        except Exception:
            pass
        else:
            msg = 'Exception for unknown extension should have been raised'
            raise Exception(msg)

        filename = unique_filename(suffix='.gml')
        try:
            read_layer(filename)
        except IOError:
            pass
        else:
            msg = 'Exception for non-existing file should have been raised'
            raise Exception(msg)

        # Read and verify test data
        for vectorname in ['lembang_schools.shp',
                           'tsunami_exposure_BB.shp']:

            filename = '%s/%s' % (TESTDATA, vectorname)
            layer = read_layer(filename)
            coords = layer.get_geometry()
            attributes = layer.get_data()

            # Check basic data integrity
            N = len(layer)
            assert coords.shape[0] == N
            assert coords.shape[1] == 2
            assert len(layer) == N

            assert isinstance(layer.get_name(), basestring)

            # Check projection
            wkt = layer.get_projection(proj4=False)
            assert wkt.startswith('GEOGCS')

            assert layer.projection == Projection(DEFAULT_PROJECTION)

            # Check integrity of each feature
            field_names = None
            for i in range(N):
                # Consistency between of geometry and fields

                x1 = coords[i, 0]
                x2 = attributes[i]['LONGITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                x1 = coords[i, 1]
                x2 = attributes[i]['LATITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                # Verify that each feature has the same fields
                if field_names is None:
                    field_names = attributes[i].keys()
                else:
                    assert len(field_names) == len(attributes[i].keys())
                    assert field_names == attributes[i].keys()

            # Write data back to file
            # FIXME (Ole): I would like to use gml here, but OGR does not
            #              store the spatial reference!
            out_filename = unique_filename(suffix='.shp')
            write_point_data(attributes, wkt, coords, out_filename)

            # Read again and check
            layer = read_layer(out_filename)
            coords = layer.get_geometry()
            attributes = layer.get_data()

            # Check basic data integrity
            N = len(layer)
            assert coords.shape[0] == N
            assert coords.shape[1] == 2

            # Check projection
            assert layer.projection == Projection(DEFAULT_PROJECTION)

            # Check integrity of each feature
            field_names = None
            for i in range(N):

                # Consistency between of geometry and fields
                x1 = coords[i, 0]
                x2 = attributes[i]['LONGITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                x1 = coords[i, 1]
                x2 = attributes[i]['LATITUDE']
                assert x2 is not None
                msg = 'Inconsistent longitudes: %f != %f' % (x1, x2)
                assert numpy.allclose(x1, x2), msg

                # Verify that each feature has the same fields
                if field_names is None:
                    field_names = attributes[i].keys()
                else:
                    assert len(field_names) == len(attributes[i].keys())
                    assert field_names == attributes[i].keys()

            # Test individual extraction
            lon = layer.get_data(attribute='LONGITUDE')
            assert numpy.allclose(lon, coords[:, 0])

    def test_analysis_of_vector_data_top_N(self):
        """Analysis of vector data - get top N of an attribute
        """

        for vectorname in ['lembang_schools.shp',
                           'tsunami_exposure_BB.shp']:

            filename = '%s/%s' % (TESTDATA, vectorname)
            layer = read_layer(filename)
            coords = layer.get_geometry()
            attributes = layer.get_data()

            # Check exceptions
            try:
                L = layer.get_topN(attribute='FLOOR_AREA', N=0)
            except AssertionError:
                pass
            else:
                msg = 'Exception should have been raised for N == 0'
                raise Exception(msg)

            # Check results
            for N in [5, 10, 11, 17]:
                if vectorname == 'lembang_schools.shp':
                    L = layer.get_topN(attribute='FLOOR_AREA', N=N)
                    assert len(L) == N
                    assert L.get_projection() == layer.get_projection()
                    #print [a['FLOOR_AREA'] for a in L.attributes]
                elif vectorname == 'tsunami_exposure_BB.shp':
                    L = layer.get_topN(attribute='STR_VALUE', N=N)
                    assert len(L) == N
                    assert L.get_projection() == layer.get_projection()
                    val = [a['STR_VALUE'] for a in L.data]

                    ref = [a['STR_VALUE'] for a in attributes]
                    ref.sort()

                    assert numpy.allclose(val, ref[-N:],
                                          atol=1.0e-12, rtol=1.0e-12)
                else:
                    raise Exception

    def test_vector_class(self):
        """Consistency of vector class for point data
        """

        # Read data file
        layername = 'lembang_schools.shp'
        filename = '%s/%s' % (TESTDATA, layername)
        V = read_layer(filename)

        # Make a smaller dataset
        V_ref = V.get_topN('FLOOR_AREA', 5)

        geometry = V_ref.get_geometry()
        data = V_ref.get_data()
        projection = V_ref.get_projection()

        # Create new object from test data
        V_new = Vector(data=data, projection=projection, geometry=geometry)

        # Check
        assert V_new == V_ref
        assert not V_new != V_ref

        # Write this new object, read it again and check
        tmp_filename = unique_filename(suffix='.shp')
        V_new.write_to_file(tmp_filename)

        V_tmp = read_layer(tmp_filename)
        assert V_tmp == V_ref
        assert not V_tmp != V_ref

        # Check that equality raises exception when type is wrong
        try:
            V_tmp == Raster()
        except TypeError:
            pass
        else:
            msg = 'Should have raised TypeError'
            raise Exception(msg)

    def test_rasters_and_arrays(self):
        """Consistency of rasters and associated arrays
        """

        # Create test data
        lon_ul = 100  # Longitude of upper left corner
        lat_ul = 10   # Latitude of upper left corner
        numlon = 8    # Number of longitudes
        numlat = 5    # Number of latitudes
        dlon = 1
        dlat = -1

        # Define array where latitudes are rows and longitude columns
        A1 = numpy.zeros((numlat, numlon))

        # Establish coordinates for lower left corner
        lat_ll = lat_ul - numlat
        lon_ll = lon_ul

        # Define pixel centers along each direction
        lon = numpy.linspace(lon_ll + 0.5, lon_ll + numlon - 0.5, numlon)
        lat = numpy.linspace(lat_ll + 0.5, lat_ll + numlat - 0.5, numlat)

        # Define raster with latitudes going bottom-up (south to north).
        # Longitudes go left-right (west to east)
        for i in range(numlat):
            for j in range(numlon):
                A1[numlat - 1 - i, j] = linear_function(lon[j], lat[i])

        # Upper left corner
        assert A1[0, 0] == 105.25
        assert A1[0, 0] == linear_function(lon[0], lat[4])

        # Lower left corner
        assert A1[4, 0] == 103.25
        assert A1[4, 0] == linear_function(lon[0], lat[0])

        # Upper right corner
        assert A1[0, 7] == 112.25
        assert A1[0, 7] == linear_function(lon[7], lat[4])

        # Lower right corner
        assert A1[4, 7] == 110.25
        assert A1[4, 7] == linear_function(lon[7], lat[0])

        # Generate raster object and write
        projection = ('GEOGCS["WGS 84",'
                      'DATUM["WGS_1984",'
                      'SPHEROID["WGS 84",6378137,298.2572235630016,'
                      'AUTHORITY["EPSG","7030"]],'
                      'AUTHORITY["EPSG","6326"]],'
                      'PRIMEM["Greenwich",0],'
                      'UNIT["degree",0.0174532925199433],'
                      'AUTHORITY["EPSG","4326"]]')
        geotransform = (lon_ul, dlon, 0, lat_ul, 0, dlat)
        R1 = Raster(A1, projection, geotransform)

        msg = ('Dimensions of raster array do not match those of '
               'raster object')
        assert numlat == R1.rows, msg
        assert numlon == R1.columns, msg

        # Write back to new (tif) file
        out_filename = unique_filename(suffix='.tif')
        R1.write_to_file(out_filename)

        # Read again and check consistency
        R2 = read_layer(out_filename)

        msg = ('Dimensions of written raster array do not match those '
               'of input raster file\n')
        msg += ('    Dimensions of input file '
                '%s:  (%s, %s)\n' % (R1.filename, numlat, numlon))
        msg += ('    Dimensions of output file %s: '
                '(%s, %s)' % (R2.filename, R2.rows, R2.columns))

        assert numlat == R2.rows, msg
        assert numlon == R2.columns, msg

        A2 = R2.get_data()

        assert numpy.allclose(numpy.min(A1), numpy.min(A2))
        assert numpy.allclose(numpy.max(A1), numpy.max(A2))

        msg = 'Array values of written raster array were not as expected'
        assert numpy.allclose(A1, A2), msg

        msg = 'Geotransforms were different'
        assert R1.get_geotransform() == R2.get_geotransform(), msg

        p1 = R1.get_projection(proj4=True)
        p2 = R2.get_projection(proj4=True)
        msg = 'Projections were different: %s != %s' % (p1, p2)
        assert p1 == p1, msg

        # Exercise projection __eq__ method
        assert R1.projection == R2.projection

        # Check that equality raises exception when type is wrong
        try:
            R1.projection == 234
        except TypeError:
            pass
        else:
            msg = 'Should have raised TypeError'
            raise Exception(msg)

    def test_reading_and_writing_of_real_rasters(self):
        """Rasters can be read and written correctly
        """

        for rastername in ['Earthquake_Ground_Shaking_clip.tif',
                             'Population_2010_clip.tif',
                             'shakemap_padang_20090930.asc',
                             'population_padang_1.asc',
                             'population_padang_2.asc']:

            filename = '%s/%s' % (TESTDATA, rastername)
            R1 = read_layer(filename)

            # Check consistency of raster
            A1 = R1.get_data()
            M, N = A1.shape

            msg = ('Dimensions of raster array do not match those of '
                   'raster file %s' % R1.filename)
            assert M == R1.rows, msg
            assert N == R1.columns, msg

            # Write back to new (tif) file
            out_filename = unique_filename(suffix='.tif')
            write_raster_data(A1,
                              R1.get_projection(),
                              R1.get_geotransform(),
                              out_filename)

            # Read again and check consistency
            R2 = read_layer(out_filename)

            msg = ('Dimensions of written raster array do not match those '
                   'of input raster file\n')
            msg += ('    Dimensions of input file '
                    '%s:  (%s, %s)\n' % (R1.filename, M, N))
            msg += ('    Dimensions of output file %s: '
                    '(%s, %s)' % (R2.filename, R2.rows, R2.columns))

            assert M == R2.rows, msg
            assert N == R2.columns, msg

            A2 = R2.get_data()

            assert numpy.allclose(numpy.min(A1), numpy.min(A2))
            assert numpy.allclose(numpy.max(A1), numpy.max(A2))

            msg = 'Array values of written raster array were not as expected'
            assert numpy.allclose(A1, A2), msg

            msg = 'Geotransforms were different'
            assert R1.get_geotransform() == R2.get_geotransform(), msg

            p1 = R1.get_projection(proj4=True)
            p2 = R2.get_projection(proj4=True)
            msg = 'Projections were different: %s != %s' % (p1, p2)
            assert p1 == p1, msg

            # Use overridden == and != to verify
            assert R1 == R2
            assert not R1 != R2

            # Check that equality raises exception when type is wrong
            try:
                R1 == Vector()
            except TypeError:
                pass
            else:
                msg = 'Should have raised TypeError'
                raise Exception(msg)

    def test_no_projection(self):
        """Raster layers with no projection causes Exception to be raised
        """

        rastername = 'grid_without_projection.asc'
        filename = '%s/%s' % (TESTDATA, rastername)
        try:
            read_layer(filename)
        except RuntimeError:
            pass
        else:
            msg = 'Should have raised RuntimeError'
            raise Exception(msg)

    def test_nodata_value(self):
        """NODATA value is correctly recorded in GDAL
        """

        # Read files with -9999 as nominated nodata value
        for rastername in ['Population_2010_clip.tif',
                           'Lembang_Earthquake_Scenario.asc',
                           'Earthquake_Ground_Shaking.asc']:

            filename = '%s/%s' % (TESTDATA, rastername)
            R = read_layer(filename)

            A = R.get_data()

            # Verify nodata value
            Amin = min(A.flat[:])
            msg = ('Raster must have -9999 as its minimum for this test. '
                   'We got %f for file %s' % (Amin, filename))
            assert Amin == -9999, msg

            # Verify that GDAL knows about this
            nodata = R.get_nodata_value()
            msg = ('File %s should have registered nodata '
                   'value %i but it was %s' % (filename, Amin, nodata))
            assert nodata == Amin, msg

    def test_vector_extrema(self):
        """Vector extremum calculation works
        """

        for layername in ['lembang_schools.shp',
                          'tsunami_exposure_BB.shp']:

            filename = '%s/%s' % (TESTDATA, layername)
            L = read_layer(filename)

            if layername == 'tsunami_exposure_BB.shp':
                attributes = L.get_data()

                for name in ['STR_VALUE', 'CONT_VALUE']:
                    minimum, maximum = L.get_extrema(name)
                    assert minimum <= maximum

                    x = [a[name] for a in attributes]
                    assert numpy.allclose([min(x), max(x)],
                                          [minimum, maximum],
                                          rtol=1.0e-12, atol=1.0e-12)

            elif layername == 'lembang_schools.shp':
                minimum, maximum = L.get_extrema('FLOOR_AREA')
                assert minimum == maximum  # All identical
                assert maximum == 250

                try:
                    L.get_extrema('NONEXISTING_ATTRIBUTE_NAME_8462')
                except AssertionError:
                    pass
                else:
                    msg = ('Non existing attribute name should have '
                           'raised AssertionError')
                    raise Exception(msg)

                try:
                    L.get_extrema()
                except RuntimeError:
                    pass
                else:
                    msg = ('Missing attribute name should have '
                           'raised RuntimeError')
                    raise Exception(msg)

    def test_raster_extrema(self):
        """Raster extrema (including NAN's) are correct.
        """

        for rastername in ['Earthquake_Ground_Shaking_clip.tif',
                             'Population_2010_clip.tif',
                             'shakemap_padang_20090930.asc',
                             'population_padang_1.asc',
                             'population_padang_2.asc']:

            filename = '%s/%s' % (TESTDATA, rastername)
            R = read_layer(filename)

            # Check consistency of raster

            # Use numpy to establish the extrema instead of gdal
            minimum, maximum = R.get_extrema()

            # Check that arrays with NODATA value replaced by NaN's agree
            A = R.get_data(nan=False)
            B = R.get_data(nan=True)

            assert A.dtype == B.dtype
            assert numpy.nanmax(A - B) == 0
            assert numpy.nanmax(B - A) == 0
            assert numpy.nanmax(numpy.abs(A - B)) == 0

            # Check that extrema are OK
            assert numpy.allclose(maximum, numpy.max(A[:]))
            assert numpy.allclose(maximum, numpy.nanmax(B[:]))
            assert numpy.allclose(minimum, numpy.nanmin(B[:]))

            # Check that nodata can be replaced by 0.0
            C = R.get_data(nan=0.0)
            msg = '-9999 should have been replaced by 0.0 in %s' % rastername
            assert min(C.flat[:]) != -9999, msg

    def test_bins(self):
        """Linear and quantile bins are correct
        """

        for filename in ['%s/population_padang_1.asc' % TESTDATA,
                         '%s/test_grid.asc' % TESTDATA]:

            R = read_layer(filename)
            min, max = R.get_extrema()

            for N in [2, 3, 5, 7, 10, 16]:
                linear_intervals = R.get_bins(N=N, quantiles=False)

                assert linear_intervals[0] == min
                assert linear_intervals[-1] == max

                d = (max - min) / N
                for i in range(N):
                    assert numpy.allclose(linear_intervals[i], min + i * d)

                quantiles = R.get_bins(N=N, quantiles=True)
                A = R.get_data(nan=True).flat[:]

                mask = numpy.logical_not(numpy.isnan(A))  # Omit NaN's
                l1 = len(A)
                A = A.compress(mask)
                l2 = len(A)

                if filename == '%s/test_grid.asc' % TESTDATA:
                    # Check that NaN's were removed
                    assert l1 == 35
                    assert l2 == 30

                # Assert that there are no NaN's
                assert not numpy.alltrue(numpy.isnan(A))

                number_of_elements = len(A)
                average_elements_per_bin = number_of_elements / N

                # Count elements in each bin and check
                i0 = quantiles[0]
                for i1 in quantiles[1:]:
                    count = numpy.sum((i0 < A) & (A < i1))
                    if i0 == quantiles[0]:
                        refcount = count

                    if i1 < quantiles[-1]:
                        # Number of elements in each bin must vary by no
                        # more than 1
                        assert abs(count - refcount) <= 1
                        assert abs(count - average_elements_per_bin) <= 3
                    else:
                        # The last bin is allowed vary by more
                        pass

                    i0 = i1

    def test_get_bounding_box(self):
        """Bounding box is correctly extracted from file.

        # Reference data:
        gdalinfo Earthquake_Ground_Shaking_clip.tif
        Driver: GTiff/GeoTIFF
        Files: Earthquake_Ground_Shaking_clip.tif
        Size is 345, 263
        Coordinate System is:
        GEOGCS["WGS 84",
            DATUM["WGS_1984",
                SPHEROID["WGS 84",6378137,298.2572235630016,
                    AUTHORITY["EPSG","7030"]],
                AUTHORITY["EPSG","6326"]],
            PRIMEM["Greenwich",0],
            UNIT["degree",0.0174532925199433],
            AUTHORITY["EPSG","4326"]]
        Origin = (99.364169565217395,-0.004180608365019)
        Pixel Size = (0.008339130434783,-0.008361216730038)
        Metadata:
          AREA_OR_POINT=Point
          TIFFTAG_XRESOLUTION=1
          TIFFTAG_YRESOLUTION=1
          TIFFTAG_RESOLUTIONUNIT=1 (unitless)
        Image Structure Metadata:
          COMPRESSION=LZW
          INTERLEAVE=BAND
        Corner Coordinates:
        Upper Left  (  99.3641696,  -0.0041806) ( 99d21'51.01"E,  0d 0'15.05"S)
        Lower Left  (  99.3641696,  -2.2031806) ( 99d21'51.01"E,  2d12'11.45"S)
        Upper Right ( 102.2411696,  -0.0041806) (102d14'28.21"E,  0d 0'15.05"S)
        Lower Right ( 102.2411696,  -2.2031806) (102d14'28.21"E,  2d12'11.45"S)
        Center      ( 100.8026696,  -1.1036806) (100d48'9.61"E,  1d 6'13.25"S)
        Band 1 Block=256x256 Type=Float64, ColorInterp=Gray

        """

        ref_bbox = {'tsunami_exposure_BB.shp': [150.124,
                                                -35.7856,
                                                150.295,
                                                -35.6546],
                    'Earthquake_Ground_Shaking_clip.tif': [99.3641696,
                                                           -2.2031806,
                                                           102.2411696,
                                                           -0.0041806]}

        for filename in ['Earthquake_Ground_Shaking_clip.tif',
                         'tsunami_exposure_BB.shp']:
            bbox = get_bounding_box(os.path.join(TESTDATA, filename))
            assert numpy.allclose(bbox, ref_bbox[filename])

    def test_layer_API(self):
        """Vector and Raster instances have a similar API
        """

        # Exceptions
        exclude = ['get_topN', 'get_bins',
                   'get_geotransform', 'get_nodata_value']

        V = Vector()  # Empty vector instance
        R = Raster()  # Empty raster instance

        assert same_API(V, R, exclude=exclude)

        for layername in ['lembang_schools.shp',
                          'Lembang_Earthquake_Scenario.asc']:

            filename = '%s/%s' % (TESTDATA, layername)
            L = read_layer(filename)

            assert same_API(L, V, exclude=exclude)
            assert same_API(L, R, exclude=exclude)


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_IO, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
