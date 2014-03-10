# Django settings for ShoghlanahProject project.

import dj_database_url
import os

gettext = lambda s: s

PROJECT_DIR = os.path.dirname(__file__)


LOCALE_PATHS = ( os.path.join(PROJECT_DIR, 'locale' ), )

DEBUG = True
SEND_BROKEN_LINK_EMAILS = DEBUG
TEMPLATE_DEBUG = DEBUG
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/log_in/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_EXPIRE_AFTER = 3600
SESSION_SECURITY_WARN_AFTER = 3605
ADMINS = (
    ('Salma Hamed', 'shamed@morabiz.com'), ('Mahmoud Abdrabo', 'mabdrabo@morabiz.com'), ('Mohannad Banayosi', 'mbanayosi@morabiz.com'),
    ('Tarek Sheasha', 'tsheasha@morabiz.com'), ('Fady Kamal', 'fkamal@morabiz.com'),
)

if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.config(default=os.environ['DATABASE_URL'])}

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'shoghlanah_db',                      # Or path to database file if using sqlite3.
            'USER': 'django_postgres',                      # Not used with sqlite3.
            'PASSWORD': '1234',                  # Not used with sqlite3.
            'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

"""
if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.config(default=os.environ['DATABASE_URL'])}

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'd193qt75duldg5',                      # Or path to database file if using sqlite3.
            'USER': 'ukylfsusnkqcyj',                      # Not used with sqlite3.
            'PASSWORD': 'ISGIoj7_y5Q4afE99sU2pqsWAH',                  # Not used with sqlite3.
            'HOST': 'ec2-54-243-235-7.compute-1.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
        }
    }
"""


# DATABASES = {'default': dj_database_url.config(default='postgres://foo:bar@localhost:5432/db')}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Egypt'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'
LANGUAGES = (( 'ar', gettext( 'Arabic' ) ), ( 'en', gettext( 'English' ) ), )
LANGUAGES_BIDI = ( "ar", )


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True
# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join( PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
# STATIC_ROOT = os.path.join( PROJECT_DIR, 'static')
STATIC_URL = '/static/'

# to use Amazon S3 storage
# DEFAULT_FILE_STORAGE = 'ShoghlanahProject.shoghlanah.s3utils.MediaS3BotoStorage'
# STATICFILES_STORAGE = 'ShoghlanahProject.shoghlanah.s3utils.StaticS3BotoStorage'
# STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

# Additional locations of static files

    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = (os.path.join(PROJECT_DIR, 'static'),)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'eapto#s1_e$e$28xp(_=j73+1oy3y))(ggc(-(_v2-67&amp;dbtj^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'currentTemplate.CurrentTemplateMiddleware.CurrentTemplateMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ShoghlanahProject.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ShoghlanahProject.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join( os.path.dirname( __file__ ), 'templates' ),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "shoghlanah.context_processors.settings",
)

TEMPLATE_VISIBLE_SETTINGS = (
    'DEPLOYED_ADDRESS',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'tagging',  # Tagging Module used for Skills tags.
    'shoghlanah',
    'userprofiles',
    'userprofiles.contrib.accountverification',
    'userprofiles.contrib.emailverification',
    'userprofiles.contrib.profiles',
    'haystack',
    'notification',
    'actstream',
    'sorl.thumbnail',
    'storages',
    'gunicorn',
    # 'south',
    'session_security',
    'currentTemplate',
)
USERPROFILES_EMAIL_ONLY = True
USERPROFILES_CHECK_UNIQUE_EMAIL = True
#USERPROFILES_REGISTRATION_FORM = 'shoghlanah.forms.ProfileRegistrationForm'
USERPROFILES_USE_ACCOUNT_VERIFICATION = True
USERPROFILES_USE_PROFILE = True
USERPROFILES_AUTO_LOGIN = False
#USERPROFILES_ACCOUNT_VERIFICATION_DAYS = 7

AUTHENTICATION_BACKENDS = (
    'userprofiles.auth_backends.EmailOrUsernameModelBackend',
    'shoghlanah.facebook.FacebookBackend',
    'shoghlanah.linkedin.LinkedinBackend',
    'shoghlanah.twitter.TwitterBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_PROFILE_MODULE = 'shoghlanah.UserProfile'

EMAIL_USE_TLS = True
EMAIL_PORT = 587
if not DEBUG:
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
else:
    EMAIL_HOST = 'smtp.gmail.com'
    # EMAIL_HOST_USER = 'info@shoghlanah'  # SendGrid
    EMAIL_HOST_USER = 'info.shoghlanah@gmail.com'
    EMAIL_HOST_PASSWORD = 'deaf200cab'
SERVER_EMAIL = EMAIL_HOST_USER

PUSHER_APP_ID = '26078'
PUSHER_KEY = 'bbb92b9f5ce229452bee'
PUSHER_SECRET = '9f11b98f08fdd70318d6'


# Haystack settings
if not DEBUG:
    url = os.environ['SEARCHBOX_URL']
    index_name = os.environ['SEARCHBOX_INDEX']
else:
    url = 'http://127.0.0.1:9200/'
    index_name = 'haystack'


HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': url,
        'INDEX_NAME': index_name,
    },
}
#HAYSTACK_CONNECTIONS = {
#    'default': {
#       'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
#       'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
#   },
#}
#HAYSTACK_SITECONF = 'shoghlanah.search_indexes'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')
#HAYSTACK_SITECONFNCLUDE_SPELLING = True
#HAYSTACK_DEFAULT_OPERATOR = 'OR'


#Tagging Jquery
TAGGING_AUTOCOMPLETE_JS_BASE_URL = '/static/js/jquery-autocomplete'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

if not DEBUG:
    # DEPLOYED_ADDRESS = 'http://www.shoghlanah.com/'  # main deployed version
    DEPLOYED_ADDRESS = 'http://deafcab-test.herokuapp.com/'  # testing deployed version
    # DEPLOYED_ADDRESS = 'http://deafcab-mabdrabo.herokuapp.com/'  # mabdrabo deployed version
else:
    DEPLOYED_ADDRESS = 'http://127.0.0.1:8000/'  # Localhost address

if not DEBUG:
    # FACEBOOK_ID = '485348228180335'  # Deployment ID
    # FACEBOOK_SECRET = '1c8e83f263771522902925539fbf2742'  # Deployment SECRET
    FACEBOOK_ID = '130615207082415'  # Testing ID
    FACEBOOK_SECRET = '84113eb3adc75807fd14823ce86afe27'  # Testing SECRET
else:
    FACEBOOK_ID = '361581283917473'   # Localhost ID
    FACEBOOK_SECRET = '1f9b16aa6d5ff80bfbd3670c0d77e479'  # Localhost SECRET
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_about_me', 'friends_photos', 'publish_actions', 'publish_actions']

TWITTER_KEY = 'PZChQ8ZWFb4vCvb86Kuo8w'
TWITTER_SECRET = '3eh5IGZ7eTPPxM0r8vjbAFAD5lNhncMAFnsYFrS1g'

LINKEDIN_ID = 'm3wzm8m46hsk'
LINKEDIN_SECRET = 'f5AyuM49P8xabAFC'
LINKEDIN_PERMISSIONS = ['r_basicprofile', 'r_emailaddress']

GOOGLE_ID = '657005916412.apps.googleusercontent.com'
GOOGLE_SECRET = 'YWKJuY4MpCSS2CXSvgVmaW4x'


THUMBNAIL_DEBUG = DEBUG

# Stripe keys
# Testing keys
STRIPE_PUBLISHABLE = 'pk_test_dbdATN0fpihQipdGbs3KsMgz'
STRIPE_SECRET = 'sk_test_BCK0PAFAzrYSem9UXoiMBhfy'

# THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.convert_engine.Engine'

if not DEBUG:
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    DEFAULT_FILE_STORAGE = 'shoghlanah.s3utils.DefaultStorage'
    STATICFILES_STORAGE = 'shoghlanah.s3utils.StaticStorage'
    # THUMBNAIL_PREFIX = 'media/cache/'
    S3_URL = 'http://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    DEFAULT_S3_PATH = "media"
    STATIC_S3_PATH = "static"
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = S3_URL + STATIC_ROOT
    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = S3_URL + MEDIA_ROOT
