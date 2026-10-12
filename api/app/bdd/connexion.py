from contextlib import contextmanager
import mysql.connector as mysqlpyth
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


class Connexion:
    @staticmethod
    @contextmanager
    def ouvrir_connexion():
        bdd = mysqlpyth.connect(
            user=DB_USER, password=DB_PASSWORD, host=DB_HOST,
            port=int(DB_PORT), database=DB_NAME, connection_timeout=5,
        )
        try:
            cursor = bdd.cursor(dictionary=True)
            try:
                yield bdd, cursor
            finally:
                cursor.close()
        finally:
            bdd.close()
