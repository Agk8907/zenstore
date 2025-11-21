import dj_database_url
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-upgrade-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'cloudinary_storage',
    'cloudinary',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zenstore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'zenstore.wsgi.application'



AUTH_USER_MODEL = 'store.User'

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True







DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ==============================================
# ZENSTORE: PAYMENT & EMAIL CONFIGURATION
# ==============================================

import os

# RAZORPAY SETTINGS (Get these from https://dashboard.razorpay.com/app/keys)
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_HERE'  # <--- REPLACE THIS
RAZORPAY_KEY_SECRET = 'YOUR_SECRET_HERE'    # <--- REPLACE THIS

# EMAIL SETTINGS (Using Gmail as example)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'    # <--- REPLACE THIS
EMAIL_HOST_PASSWORD = 'your-app-password'   # <--- REPLACE THIS (Use App Password, not login password)



# DATABASE CONFIGURATION
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# SECURITY CONFIG
if 'RENDER' in os.environ:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-insecure-key')

# ==============================================
# CLOUDINARY STORAGE (FOR IMAGES ON RENDER)
# ==============================================
import os

# Only use Cloudinary if keys are present (Production)
if 'CLOUDINARY_CLOUD_NAME' in os.environ:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    # Tell Django to use Cloudinary for 'ImageField'
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Localhost fallback
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==============================================
# CLOUDINARY STORAGE (FORCED FOR RENDER)
# ==============================================
import os

# Check if we are running on Render
if 'RENDER' in os.environ:
    print("--- PRODUCTION MODE DETECTED: ENABLING CLOUDINARY ---")
    
    # 1. Ensure Cloudinary Apps are loaded
    INSTALLED_APPS += [
        
        
    ]

    # 2. Configure Keys
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }

    # 3. Force Django to use Cloudinary for Images
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # 4. Print for debugging (Check Render Logs if this fails)
    if not CLOUDINARY_STORAGE['CLOUD_NAME']:
        print("!!! WARNING: CLOUDINARY_CLOUD_NAME IS MISSING in Environment Variables !!!")

else:
    # Localhost settings
    print("--- LOCAL MODE: USING HARD DRIVE STORAGE ---")
    MEDIA_URL = '/images/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')


# ==============================================
# ROBUST MEDIA CONFIGURATION
# ==============================================
import os

# Force Cloudinary on Render
if 'RENDER' in os.environ:
    print("--- SETTINGS: CONFIGURING CLOUDINARY ---")
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Ensure we don't use local URLs
    MEDIA_URL = 'https://res.cloudinary.com/' + os.environ.get('CLOUDINARY_CLOUD_NAME') + '/'
    
else:
    print("--- SETTINGS: CONFIGURING LOCAL STORAGE ---")
    MEDIA_URL = '/images/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')


# ==============================================
# STATIC FILES (CSS/JS) CONFIGURATION
# ==============================================


if not DEBUG:
    # Production (Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Localhost
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]


# ==============================================
# STATIC FILES CONFIGURATION (CSS/JS)
# ==============================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Production Settings (Render)
if 'RENDER' in os.environ:
    # Tell Django where to copy files for deployment
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    
    # Enable WhiteNoise to compress and cache files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Local settings
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_local')
