const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const APP_NAME = 'zenstore'; // The folder containing settings.py

console.log("=== REVERTING TO LOCALHOST VERSION (REMOVING DEPLOYMENT CONFIGS) ===");

// --- 1. RESTORE CLEAN SETTINGS.PY ---
const settingsContent = `
"""
Django settings for zenstore project.
RESTORED TO LOCAL DEVELOPMENT VERSION.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-reverted-local-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store', # Your Main App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CSS/JS) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# --- MEDIA FILES (IMAGES) - LOCAL STORAGE ---
MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/images')

# --- CUSTOM USER MODEL ---
AUTH_USER_MODEL = 'store.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# RAZORPAY CONFIG (Keep these if you want to test payments locally)
# Replace with your TEST keys if needed
RAZORPAY_KEY_ID = 'rzp_test_YOUR_ID_HERE'
RAZORPAY_KEY_SECRET = 'YOUR_SECRET_HERE'

# EMAIL CONFIG (Keep for local testing)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
`;

const settingsPath = path.join(PROJECT_ROOT, APP_NAME, 'settings.py');
fs.writeFileSync(settingsPath, settingsContent);
console.log("✅ settings.py restored to Local Mode (SQLite + Local Images).");

// --- 2. DELETE DEPLOYMENT FILES ---
const filesToDelete = ['build.sh', 'Procfile', 'render.yaml'];

filesToDelete.forEach(file => {
    const filePath = path.join(PROJECT_ROOT, file);
    if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        console.log(`🗑️  Deleted deployment file: ${file}`);
    }
});

// --- 3. CLEAN REQUIREMENTS.TXT ---
// We remove gunicorn, whitenoise, psycopg2, cloudinary
const reqPath = path.join(PROJECT_ROOT, 'requirements.txt');
if (fs.existsSync(reqPath)) {
    const localReqs = `
asgiref
Django
Pillow
pytz
razorpay
sqlparse
    `.trim();
    fs.writeFileSync(reqPath, localReqs);
    console.log("✅ requirements.txt restored to local dependencies.");
}

console.log("\n=======================================");
console.log("       BACK TO LOCALHOST! 🏠");
console.log("=======================================");
console.log("1. Your project is now running on SQLite3 again.");
console.log("2. Images will load from your local folder.");
console.log("3. CSS will load instantly.");
console.log("4. Run: python manage.py runserver");