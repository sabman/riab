"""Miscellaneous utility functions for Risk-in-a-Box (riab_core)
"""
import os
import sys
import numpy
from osgeo import ogr, gdal
from tempfile import mkstemp

# Map between extensions and ORG drivers
driver_map = {'.shp': 'ESRI Shapefile',
              '.gml': 'GML',
              '.tif': 'GTiff'}

# Map between Python types and OGR field types
# FIXME (Ole): I can't find a double precision type for OGR
type_map = {type(''): ogr.OFTString,
            type(0): ogr.OFTInteger,
            type(0.0): ogr.OFTReal,
            type(numpy.array([0.0])[0]): ogr.OFTReal,  # numpy.float64
            type(numpy.array([[0.0]])[0]): ogr.OFTReal}  # numpy.ndarray

# The projection string depends on the gdal version
DEFAULT_PROJECTION = '+proj=longlat +datum=WGS84 +no_defs'

# A maximum floating point number for this package
MAXFLOAT = float(sys.maxint)


# Miscellaneous auxiliary functions
def unique_filename(suffix=None):
    """Create new filename guarenteed not to exist previoously

    Use mkstemp to create the file, then remove it and return the name
    """

    _, filename = mkstemp(suffix=suffix)

    try:
        os.remove(filename)
    except:
        pass

    return filename


# GeoServer utility functions
# TODO: Should really be in Gdal or lower level API

WFS_NAMESPACE = '{http://www.opengis.net/wfs}'
WCS_NAMESPACE = '{http://www.opengis.net/wcs}'


def get_layers_metadata(url, version, feature=None):
    '''
    Return the metadata for each layers as an dict formed from the keywords

    Assumes the format for the keywords is "identifier:value"

    default searches both feature and raster layers by default
      Input
        url: The wfs url
        version: The version of the wfs xml expected
        feature: None=both,True=Feature,False=Raster

      Returns
        Hash containing the keywords for the layer

        based on OWSLib vs 2.0.0.
        http://trac.gispython.org/lab/browser/OWSLib/...
              trunk/owslib/feature/wfs200.py#L402
    '''
    if not feature:
        typelist = 'ContentMetadata'
        typeelms = 'CoverageOfferingBrief'
        namestr = 'name'
        titlestr = 'label'
        NAMESPACE = WCS_NAMESPACE
        keywordstr = 'keywords'
        abstractstr = 'description'
        keywords_base = {'layerType': 'raster'}
    else:
        typelist = 'FeatureTypeList'
        typeelms = 'FeatureType'
        namestr = 'Name'
        titlestr = 'Title'
        abstractstr = 'Abstract'
        NAMESPACE = WFS_NAMESPACE
        keywordstr = 'Keywords'
        keywords_base = {'layerType': 'feature'}

    if feature == None:
        layers = get_layers_metadata(url, version, feature=False)  # raster
        layers.extend(get_layers_metadata(url, version, feature=True))
        return layers

    _capabilities = WFSCapabilitiesReader(version).read(url, feature)

    layers = []
    serviceidentelem = _capabilities.find(NAMESPACE + 'Service')

    featuretypelistelem = _capabilities.find(NAMESPACE + typelist)
    featuretypeelems = featuretypelistelem.findall(NAMESPACE + typeelms)
    for f in featuretypeelems:
        keywords = keywords_base.copy()
        name = f.findall(NAMESPACE + namestr)
        title = f.findall(NAMESPACE + titlestr)
        kwds = f.findall(NAMESPACE + keywordstr)
        abstract = f.findall(NAMESPACE + abstractstr)

        keywords['title'] = title[0].text
        layer_name = name[0].text

        if feature == False:
            kwds = kwds[0].findall(NAMESPACE + 'keyword')
        if kwds is not None:
            for kwd in kwds[:]:
                #split all the kepairs
                keypairs = str(kwd.text).split(',')
                for val in keypairs:
                    # only use keywords containing at least one :
                    if str(val).find(':') > -1:
                        k, v = val.split(':')
                        keywords[k.strip()] = v.strip()

        # Also allow for keywords to be set in the abstract
        if abstract is not None and len(abstract) > 0:
            assert len(abstract) == 1
            abstract_text = abstract[0].text
            # only use keywords containing at least one :
            if str(abstract_text).find(':') > -1:
                #split out the options
                keypairs = str(abstract_text).split(',')
                #split all the kepairs
                for val in keypairs:
                    k, v = val.split(':')
                    keywords[k.strip()] = v.strip()
        layers.append([layer_name, keywords])
    return layers


##### Taken from
##### http://tra.gispython.org/lab/browser/OWSLib...
##### /trunk/owslib/feature/wfs200.py#L402

import cgi
from cStringIO import StringIO
from urllib import urlencode
from urllib2 import urlopen

from owslib.wfs import WebFeatureService
from owslib.ows import ServiceIdentification, ServiceProvider
from owslib.ows import OperationsMetadata
from owslib.etree import etree
from owslib.util import nspath, testXMLValue


class WFSCapabilitiesReader(object):
    """Read and parse capabilities document into a lxml.etree infoset
    """

    def __init__(self, version='2.0.0'):
        """Initialize"""
        self.version = version
        self._infoset = None
        self.xml = ""

    def capabilities_url(self, service_url, feature):
        """Return a capabilities url
        """
        qs = []
        if service_url.find('?') != -1:
            qs = cgi.parse_qsl(service_url.split('?')[1])

        params = [x[0] for x in qs]

        if feature:
            ftype = 'wfs'
        else:
            ftype = 'wcs'

        if 'service' not in params:
            qs.append(('service', ftype))
        if 'request' not in params:
            qs.append(('request', 'GetCapabilities'))
        if 'version' not in params:
            qs.append(('version', self.version))

        urlqs = urlencode(tuple(qs))
        return service_url.split('?')[0] + '?' + urlqs

    def read(self, url, feature=True):
        """Get and parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        Parameters
        ----------
        url : string
            The URL to the WFS capabilities document.
        """
        request = self.capabilities_url(url, feature)
        u = urlopen(request)
        self.xml = u.read()
        #print self.xml
        return etree.fromstring(self.xml)

    def readString(self, st):
        """Parse a WFS capabilities document, returning an
        instance of WFSCapabilitiesInfoset

        string should be an XML capabilities document
        """
        if not isinstance(st, str):
            raise ValueError(
                "String must be of type string, not %s" % type(st))
        return etree.fromstring(st)

#########################################