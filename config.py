import os

from dotenv import load_dotenv

from database import get_db_connection as _get_db_connection
from database import initialize_database as _initialize_database

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DB_HOST = os.getenv("DB_HOST") or os.getenv("MYSQL_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306"))
    DB_USER = os.getenv("DB_USER") or os.getenv("MYSQL_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQL_DATABASE", "smartagri")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")
    DB_COLLATION = os.getenv("DB_COLLATION", "utf8mb4_unicode_ci")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    MARKET_API_KEY = os.getenv("MARKET_API_KEY", "")


def get_db_connection():
    connection = _get_db_connection()
    _initialize_database(connection)
    return connection
