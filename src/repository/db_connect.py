from contextlib import contextmanager
import psycopg2
from psycopg2 import Error, extensions
import os


@contextmanager
def get_cursor():
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        yield cursor
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
        print("DB_HOST =", os.getenv("DB_HOST"))
        yield None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
