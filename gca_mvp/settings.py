"""
Django settings for gca_mvp project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from os.path import abspath, dirname, join
import os
INTERNAL_IPS = ('127.0.0.1',)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p&h3t0i3n@lh+vl5l&ax5xwjy@(j^5f*v5gy&1*3-ytf*ycgwu'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     'debug_toolbar',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'django_celery_beat',
    'django_celery_results',
    'allauth.socialaccount.providers.kakao',
    'allauth.socialaccount.providers.naver',
    'supporting_business',
'corsheaders',


]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'gca_mvp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            join(BASE_DIR, 'templates'),
        ],
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

WSGI_APPLICATION = 'gca_mvp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gca_db_dev_2',
        'USER': 'gca_admin',
        'PASSWORD': 'gca1234!',
        'HOST': 'gca-db.ccol6zg20myn.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 기본 인증 백엔드
    'allauth.account.auth_backends.AuthenticationBackend',  # 추가
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


TIME_ZONE = 'Asia/Seoul'
# USE_TZ = True
# USE_L10N = True
# 타임존 설정 찾아보기 = > 프론트에서 자바스크립트로 현지화 하는게 서버에서 문제없는지


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'


TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'),)

# 디폴트 SITE의 id
# 등록하지 않으면, 각 요청 시에 host명의 Site 인스턴스를 찾습니다.
SITE_ID = 5
# 이메일 확인을 하지 않음.
SOCIALACCOUNT_EMAIL_VERIFICATION = True
LOGIN_REDIRECT_URL = "/"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGOUT_REDIRECT_URL = "/"

CELERY_BROKER_URL = 'redis://localhost:6379'  # 레디스 포트
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_NAME = "gca_sts"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'neogelon@gmail.com'
EMAIL_HOST_PASSWORD = 'ruedwiaeqwqlbezn'
EMAIL_USE_TLS = True

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': False,
        'EXCHANGE_TOKEN': True,
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'updated_time'],
    },
}

import raven

import os


RAVEN_CONFIG = {
    'dsn': 'https://b79a0ed0e08743c1a0ced3e6de943f72:6ac7dcecf49241c7b9c8626e5a2699a8@sentry.io/668403',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': "dev",
}

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = (
    'Access-Control-Allow-Origin: *',
)

SESSION_COOKIE_AGE =  60 *60 *3 #60 * 60  * 3

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
LOGIN_REDIRECT_URL = "/facebook_login.php"
ACCOUNT_AUTHENTICATED_LOGOUT_REDIRECTS = True
ACCOUNT_LOGOUT_REDIRECT_URL = "/facebook_logout.php"