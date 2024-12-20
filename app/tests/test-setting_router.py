from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from main import app
from utils import settings, logger
from router import settings_router

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.mark.order(1)
def test_get_settings(client: TestClient):
    response = client.get("/settings")
    assert response.status_code == 200, f"Fails to get settings: {response.text}"
    logger.info(response.json())
    assert response.json() is not None, f"Response is None: {response.text}"
    assert response.json().get("openai_model") is not None

@pytest.mark.order(2)
def test_update_settings(client: TestClient):
    response = client.patch("/settings", json={"openai_model": "gpt-4o"})
    assert response.status_code == 200, f"Fails to update settings: {response.text}"
    logger.info(response.json())
    assert response.json() is not None, f"Response is None: {response.text}"
    assert response.json().get("message") == "Settings updated successfully", f"Message is not correct: {response.text}"

@pytest.mark.order(3)
def test_get_models(client: TestClient):
    response = client.get("/settings/models")
    assert response.status_code == 200, f"Fails to get models: {response.text}"
    logger.info(response.json())
    assert response.json() is not None, f"Response is None: {response.text}"
    assert len(response.json().get("models")) > 0, f"Models is empty: {response.text}"

@pytest.mark.order(4)
def test_get_tags(client: TestClient):
    response = client.get("/settings/tags")
    assert response.status_code == 200, f"Fails to get tags: {response.text}"
    logger.info(response.json())
    assert response.json() is not None, f"Response is None: {response.text}"
    assert len(response.json().get("tags")) > 0, f"Tags is empty: {response.text}"
