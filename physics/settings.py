from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GROQ_CHATBOT_KEY = os.getenv('GROQ_CHATBOT_API')
GROQ_PRACTICE_KEY = os.getenv('GROQ_PRACTICE_KEY')
GROQ_ANIMATION_KEY = os.getenv('GROQ_ANIMATION_KEY')

GROQ_FACTS_KEY = os.getenv('GROQ_FACTS_API')
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_API")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_SECRET_KEY")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")


ALLOWED_HOSTS = [
'harshadkolekar.pythonanywhere.com',
'formulaverse.in',
'www.formulaverse.in'

]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


INSTALLED_APPS = [
    'formulas',
    'django_jsonform',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

]

SITE_ID = 1



SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP' : {
            'client_id' : os.getenv('GOOGLE_CLIENT_ID'),
            'secret' : os.getenv('GOOGLE_CLIENT_SECRET'),
            'key' : ''
            }
            }
            }
SOCIALACCOUNT_QUERY_EMAIL = True

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

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

ROOT_URLCONF = 'physics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'physics.wsgi.application'

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.sqlite3',
        'NAME' : '/home/HarshadKolekar/formulaverse/db.sqlite3',
        }

}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS=[
    'django.contrib.auth.backends.ModelBackend',



]



APPEND_SLASH = False

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/home/HarshadKolekar/formulaverse/static'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://harshadkolekar.pythonanywhere.com",
    "https://formulaverse.in",
    "https://www.formulaverse.in",


]

MEDIA_URL= "/files/"
MEDIA_ROOT= BASE_DIR/ "uploads"



STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
