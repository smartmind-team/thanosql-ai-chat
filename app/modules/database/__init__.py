from socket import create_connection
import sys
from pathlib import Path

import psycopg2
from psycopg2._psycopg import connection
from langchain_postgres.vectorstores import PGVector

from utils.settings import db
from utils.logger import logger


class Postgres:
    def __init__(self):
        self.con = None
        self.host = db.host
        self.port = db.port
        self.db = db.db
        self.user = db.user
        self.password = db.password
        self.vector_conn = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

        if self.test_connect():
            logger.info("Database connected")
        else:
            logger.error("Database connection failed")
            raise psycopg2.OperationalError("Database connection failed")

    def test_connect(self) -> bool:
        # check the database could be connected
        try:
            self.con = self.create_connect()
            return True
        except Exception as e:
            logger.error(e)
            return False
        finally:
            self.con.close()

    def create_connect(self) -> connection:
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.db,
            user=self.user,
            password=self.password,
        )

    def execute(query: str):
        if self.con is None:
            self.con = self.create_connect()
        cursor = self.con.cursor()
        try:
            cursor.execute(query)
            self.con.commit()
        except Exception as e:
            logger.error(e)
        finally:
            cursor.close()
            if self.con is not None:
                self.con.close()
            self.con = None

    def _null_check(self, value):
        if not value:
            return "NULL"
        return f"'{value}'"

    def _array_pg(self, value):
        if not value:
            return "NULL"
        return f"'{{{','.join(value)}}}'"

    def _preprocess_log(self, value: str):
        return value.replace("'", "'")

    def load_vector(self, embedding, name: str):
        return PGVector.from_existing_index(
            embedding=embedding, collection_name=name, connection=self.vector_conn
        )


pg = Postgres()
