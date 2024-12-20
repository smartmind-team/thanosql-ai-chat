from datetime import datetime
import pytest

from utils.logger import logger
from modules.database import pg


@pytest.mark.order(1)
def test_connect_database():
    start_time = datetime.now()
    logger.debug("Testing Database Connection")
    assert pg.test_connect()
    end_time = datetime.now()
    logger.info(f"Testing Database Connection took {end_time - start_time} seconds")


@pytest.mark.order(2)
def test_create_table():
    start_time = datetime.now()
    logger.debug("Testing Create Table")

    # 테스트 테이블 정의
    table_name = "test_table"
    columns = [
        ("id", "SERIAL PRIMARY KEY"),
        ("name", "VARCHAR(255)"),
        ("age", "INT"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
    ]

    # 테이블 생성 쿼리
    query = "CREATE TABLE IF NOT EXISTS {} ({});".format(
        table_name, ", ".join([" ".join(col) for col in columns])
    )
    result = pg.execute(query)
    assert result is None  # DDL 명령은 None을 반환

    # 테이블 존재 확인
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s;
    """
    result = pg.execute(query, (table_name,))
    assert len(result) > 0

    end_time = datetime.now()
    logger.info(f"Testing Create Table took {end_time - start_time} seconds")


@pytest.mark.order(3)
def test_insert_data():
    start_time = datetime.now()
    logger.debug("Testing Insert Data")
    
    # 테스트 데이터 삽입
    query = """
        INSERT INTO test_table (name, age) 
        VALUES (%s, %s) 
        RETURNING id;
    """
    result = pg.execute(query, ("테스트 사용자", 25))  # 튜플로 직접 전달
    assert result is not None
    assert len(result) > 0
    
    inserted_id = result[0][0]
    query = "SELECT * FROM test_table WHERE id = %s"
    result = pg.execute(query, (inserted_id,))
    assert result is not None
    assert len(result) > 0
    assert result[0][1] == "테스트 사용자"
    assert result[0][2] == 25

    end_time = datetime.now()
    logger.info(f"Testing Insert Data took {end_time - start_time} seconds")


@pytest.mark.order(4)
def test_update_data():
    start_time = datetime.now()
    logger.debug("Testing Update Data")

    # 데이터 업데이트
    query = """
        UPDATE test_table 
        SET age = %s 
        WHERE name = %s 
        RETURNING id;
    """
    result = pg.execute(query, (30, "테스트 사용자"))
    assert len(result) > 0

    # 업데이트된 데이터 확인
    query = "SELECT age FROM test_table WHERE name = %s;"
    result = pg.execute(query, ("테스트 사용자",))
    assert len(result) > 0
    assert result[0][0] == 30

    end_time = datetime.now()
    logger.info(f"Testing Update Data took {end_time - start_time} seconds")


@pytest.mark.order(5)
def test_delete_table():
    start_time = datetime.now()
    logger.debug("Testing Delete Table")

    # 테이블 삭제
    query = "DROP TABLE IF EXISTS test_table;"
    result = pg.execute(query)
    assert result is None  # DDL 명령은 None을 반환

    # 테이블 삭제 확인
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'test_table';
    """
    result = pg.execute(query)
    assert len(result) == 0

    end_time = datetime.now()
    logger.info(f"Testing Delete Table took {end_time - start_time} seconds")
