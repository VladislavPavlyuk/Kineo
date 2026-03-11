import os
from pathlib import Path

# load_dotenv читає змінні оточення з файлу .env
# Це зручно, щоб тримати секрети поза git.
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Підтягуємо змінні з .env, щоб не хардкодити секрети в коді
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-fallback")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
# Можна передати кілька хостів через кому в .env
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    # Базові django-додатки (адмінка, авторизація, сесії тощо)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # DRF для API
    "rest_framework",
    # CORS для запитів з фронтенду (інший домен/порт)
    "corsheaders",
    # Наш основний застосунок
    "kineo",
]

MIDDLEWARE = [
    # Порядок middleware важливий, бо вони обробляються зверху вниз.
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "kineo.context_processors.auth_groups",
            ],
        },
    },
]

ROOT_URLCONF = "kineo_project.urls"
WSGI_APPLICATION = "kineo_project.wsgi.application"

DATABASES = {
    "default": {
        # Для локальної розробки використовується SQLite файл
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "movie_list"
LOGOUT_REDIRECT_URL = "movie_list"

CORS_ALLOW_ALL_ORIGINS = True
# Для dev це зручно, але для production краще вказати конкретні домени.

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Токенна авторизація через JWT
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # За замовчуванням доступ відкритий, а обмеження задаються у view/permissions
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}
