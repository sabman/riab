# Django settings for GeoNode project.
import os
import geonode

# FIXME (Ole): What's this all about?
_ = lambda x: x

DEBUG = True
SITENAME = 'Risk In A Box'
SITEURL = 'http://localhost:8000/'
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
GEONODE_ROOT = os.path.dirname(geonode.__file__)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
                         'NAME': os.path.join(PROJECT_ROOT, 'development.db'),
                         'TEST_NAME': os.path.join(PROJECT_ROOT,
                                                   'development.db')}}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'id'

LANGUAGES = (
    ('id', _('Indonesian')),
    ('en', _('English')),
)

SITE_ID = 1

# Setting a custom test runner to avoid running the tests for
# some problematic 3rd party apps
TEST_RUNNER = 'risiko.tests.runner.RisikoTestRunner'
NOSE_ARGS = [
#      '--failed',
#      '--stop',
      '--verbosity=2',
      '--cover-erase',
      '--with-doctest',
      '--nocapture',
      '--with-coverage',
      '--cover-package=risiko,impact',
      '--cover-inclusive',
#      '--cover-tests',
      '--detailed-errors',
#      '--with-xunit',
      '--with-color',
#      '--with-pdb',
      ]

#COVERAGE_EXCLUDE_MODULES = ('geonode',)

#NOSE_PLUGINS = [
#        ]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'http://media.lawrence.com', 'http://example.com/media/'
MEDIA_URL = '/site_media/media/'

# Absolute path to the directory that holds static files like app media.
# Example: '/home/media/media.lawrence.com/apps/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media', 'static')

# URL that handles the static files like app media.
# Example: 'http://media.lawrence.com'
STATIC_URL = '/media/'

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'media'),
]

GEONODE_UPLOAD_PATH = os.path.join(STATIC_URL, 'upload/')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: 'http://foo.com/media/', '/media/'.
ADMIN_MEDIA_PREFIX = os.path.join(STATIC_URL, 'admin/')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'myv-y4#7j-d*p-__@j#*3z@!y24fz8%^z2v6atuy4bo9vqr1_a'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'geonode.maps.context_processors.resource_urls',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

# This isn't required for running the geonode site,
# but it when running sites that inherit the
# geonode.settings module.
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
    os.path.join(GEONODE_ROOT, 'locale'),
    os.path.join(GEONODE_ROOT, 'maps', 'locale'),
)

ROOT_URLCONF = 'risiko.urls'

# Note that Django automatically includes the 'templates' dir in all the
# INSTALLED_APPS, se there is no need to add maps/templates or admin/templates
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    os.path.join(GEONODE_ROOT, 'templates'),
)

# The FULLY QUALIFIED url to the GeoServer instance for this GeoNode.
GEOSERVER_BASE_URL = 'http://localhost:8001/geoserver-geonode-dev/'

# The username and password for a user that can add and edit layer
# details on GeoServer
GEOSERVER_CREDENTIALS = 'foo', 'bar'

# The FULLY QUALIFIED url to the GeoNetwork instance for this GeoNode
GEONETWORK_BASE_URL = 'http://localhost:8001/geonetwork/'

# The username and password for a user with write access to GeoNetwork
GEONETWORK_CREDENTIALS = 'admin', 'admin'

AUTHENTICATION_BACKENDS = ('geonode.core.auth.GranularBackend',)

GOOGLE_API_KEY = ('ABQIAAAAkofooZxTfcCv9Wi3zzGTVxTnme5EwnLVtEDGnh-'
                  'lFVzRJhbdQhQgAhB1eT_2muZtc0dl-ZSWrtzmrw')
LOGIN_REDIRECT_URL = '/'

DEFAULT_LAYERS_OWNER = 'admin'

# Where should newly created maps be focused?
DEFAULT_MAP_CENTER = (112.3, -7.9)

# How tightly zoomed should newly created maps be?
# 0 = entire world;
# maximum zoom is between 12 and 15 (for Google Maps, coverage varies by area)
DEFAULT_MAP_ZOOM = 5

MAP_BASELAYERSOURCES = {
    'any': {'ptype': 'gx_olsource'},
    'capra': {'url': GEOSERVER_BASE_URL + 'wms'},
    'google': {'ptype': 'gx_googlesource',
               'apiKey': GOOGLE_API_KEY}}

MAP_BASELAYERS = \
    [{'source': 'any',
      'type': 'OpenLayers.Layer',
      'args': ['No background'],
      'visibility': False,
      'fixed': True,
      'group': 'background'},
     {'source':'any',
      'type': 'OpenLayers.Layer.OSM',
      'args': ['OpenStreetMap'],
      'visibility': True,
      'fixed': True,
      'group':'background'},
     {'source': 'any',
      'type': 'OpenLayers.Layer.WMS',
      'group': 'background',
      'visibility': False,
      'fixed': True,
      'args': ['bluemarble',
               'http://maps.opengeo.org/geowebcache/service/wms',
               {'layers': ['bluemarble'],
                'format': 'image/png',
                'tiled': True,
                'tilesOrigin': [-20037508.34, -20037508.34]},
               {'buffer':0}]},
     {'source': 'google',
      'group': 'background',
      'name': 'SATELLITE',
      'visibility': False,
      'fixed': True,
      }]

# NAVBAR expects a dict of dicts or a path to an ini file
NAVBAR = \
    {'maps': {'id': '%sLink',
              'item_class': '',
              'link_class': '',
              'text': 'Maps',
              'url': 'geonode.maps.views.maps'},
     'data': {'id': '%sLink',
              'item_class': '',
              'link_class': '',
              'text': 'Data',
              'url': 'geonode.maps.views.browse_data'},
     #  'index': {'id': '%sLink',
     #            'item_class': '',
     #            'link_class': '',
     #            'text': 'Featured Map',
     #            'url': 'geonode.views.index'},
     'master': {'id': '%sLink',
                'item_class': '',
                'link_class': '',
                'text': 'This page has no tab for this navigation'},
     'meta': {'active_class': 'here',
              'default_id': '%sLink',
              'default_item_class': '',
              'default_link_class': '',
              'end_class': 'last',
              'id': '%sLink',
              'item_class': '',
              'link_class': '',
              'visible': 'data\nmaps'}}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'staticfiles',
    'django_extensions',
    'registration',
    'profiles',
    'avatar',
    'geonode.core',
    'geonode.maps',
    'geonode.proxy',
    'impact',
    'django_nose',
     # FIXME: Rosetta is only compatible with Django 1.3
     # but GeoNode is not (yet)
#    'rosetta',
)


def get_user_url(u):
    """Helper function for profile module
    """

    from django.contrib.sites.models import Site
    s = Site.objects.get_current()
    return 'http://' + s.domain + '/profiles/' + u.username


ABSOLUTE_URL_OVERRIDES = {'auth.user': get_user_url}

AUTH_PROFILE_MODULE = 'maps.Contact'
REGISTRATION_OPEN = False

SERVE_MEDIA = DEBUG

GEONODE_CLIENT_LOCATION = '/media/geonode/'

# Logging debug information to a file.
import logging

for _module in ['risiko', 'geonode']:

    # Risiko logging providing high level info
    # to $RIAB_HOME/logs/risiko.log or PROJECT_ROOT/risiko.log
    if 'RIAB_HOME' in os.environ:
        log_file = os.path.join(os.environ['RIAB_HOME'],
                                'logs', 'risiko.log')
    else:
        log_file = os.path.join(PROJECT_ROOT, 'risiko.log')

    _logger = logging.getLogger(_module)
    _logger.addHandler(logging.FileHandler(log_file))
    _logger.setLevel(logging.INFO)


try:
    from local_settings import *
except ImportError:
    pass
