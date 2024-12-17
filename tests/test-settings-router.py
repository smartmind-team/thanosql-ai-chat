import sys
import requests
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

(str(Path(__file__).parents[1]))
from main import app
from utils.logger import logger
from router import settings_router


client = TestClient(app)

logger.debug("Testing Settings Router")

def test_get_settings():
    response = client.get("/settings/")
    assert response.status_code == 200
    logger.info(response.json())

    response = client.get("/settings/tags")
    assert response.status_code == 200
    logger.info(response.json())
    
    response = client.get("/settings/models")
    assert response.status_code == 200
    logger.info(response.json())

if __name__ == "__main__":
    pytest.main(["-v", __file__])