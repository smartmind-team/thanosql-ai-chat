import sys
from pathlib import Path

import pytest

(str(Path(__file__).parents[1]))
from utils.logger import logger
from modules.database import Postgres

def test_database():
    logger.debug("Testing Database")
    assert Postgres().test_connect()

if __name__ == "__main__":
    pytest.main(["-v", __file__])