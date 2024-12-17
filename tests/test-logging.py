import sys
import pytest
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from utils.logger import logger


def test_logging():
    logger.debug("Test-debug")
    logger.info("Test-info")
    logger.warning("Test-warning")
    logger.error("Test-error")
    logger.critical("Test-critical")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
