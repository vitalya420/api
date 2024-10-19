import os
from datetime import timedelta

SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGEME")
GLOBAL_SALT = os.environ.get("GLOBAL_SALT", "thissaltwillbeusedforhashing")
ACCESS_TOKEN_EXPIRE_DAYS = timedelta(days=7)
REFRESH_TOKEN_EXPIRE_DAYS = timedelta(days=14)

POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_USERNAME = os.environ.get("REDIS_USERNAME", "redis")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "redis")
