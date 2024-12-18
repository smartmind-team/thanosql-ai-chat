import sys
from pathlib import Path
from datetime import datetime

import pytest

sys.path.append(str(Path(__file__).parents[1]))
from app.utils.logger import logger
from app.modules.database import pg

def test_database():
    start_time = datetime.now()
    logger.debug("Testing Database")
    assert pg.test_connect()
    end_time = datetime.now()
    logger.debug(f"Testing Database took {end_time - start_time} seconds")

if __name__ == "__main__":
    test_database()
    # pytest.main(["-v", __file__])