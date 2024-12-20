from datetime import datetime

from utils.logger import logger
from modules.database import pg

def test_connect_database():
    start_time = datetime.now()
    logger.debug("Testing Database")
    assert pg.test_connect()
    end_time = datetime.now()
    logger.info(f"Testing Database took {end_time - start_time} seconds")
    return True

# TODO: create table test
# TODO: insert data test
# TODO: pgvector test