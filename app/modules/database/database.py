import psycopg2
from psycopg2.pool import SimpleConnectionPool
from langchain_postgres.vectorstores import PGVector

from utils import logger, settings

db = settings.db


class Postgres:
    def __init__(self):
        self.host = db.host
        self.port = db.port
        self.db = db.db
        self.user = db.user
        self.password = db.password
        self.vector_conn = f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

        # <--- Initialize Connection Pool --->
        # NOTE: If use connection pool, you don't need to create a new connection every time
        # NOTE: Only can use in single thread, beacuase using SimpleConnectionPool
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=self.host,
            port=self.port,
            dbname=self.db,
            user=self.user,
            password=self.password,
        )

        if self.test_connect():
            logger.info("Database connected")
        else:
            logger.error("Database connection failed")
            raise psycopg2.OperationalError("Database connection failed")

    # <--- Manage connection methods --->
    # NOTE: After using the connection, you must return it to the pool
    def test_connect(self) -> bool:
        conn = None
        try:
            conn = self.get_connection()
            return True
        except Exception as e:
            logger.error(e)
            return False
        finally:
            if conn:
                self.return_connection(conn)

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        if conn:
            if not conn.closed:
                conn.commit()  # If not committed, the transaction will be rolled back
            self.pool.putconn(conn)

    # <--- Execute query methods --->
    # NOTE: Prevent to SQL Injection, use the `execute` method
    def execute(self, query: str, args=None):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

            # DDL 명령어인 경우 None 반환
            if (
                query.strip()
                .upper()
                .startswith(("CREATE", "DROP", "ALTER", "TRUNCATE"))
            ):
                return None

            return cursor.fetchall()
        except Exception as e:
            logger.error(f"[Postgres] {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    # <--- pgvector methods --->
    def load_vector(self, embedding, name: str):
        return PGVector.from_existing_index(
            embedding=embedding, collection_name=name, connection=self.vector_conn
        )

    # <--- preprocessing data utilities --->
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


pg = Postgres()
