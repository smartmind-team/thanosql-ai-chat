from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from main import app
from utils import logger


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_settings(client: TestClient):
    start_time = datetime.now()
    response = client.get("/settings")
    assert response.status_code == 200, f"Fails to get settings: {response.text}"
    logger.info(f"test_get_settings: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert response.json().get("openai_model") is not None
    end_time = datetime.now()
    logger.info(f"Testing Get Settings took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


def test_update_settings(client: TestClient):
    start_time = datetime.now()
    response = client.patch("/settings", json={"openai_model": "gpt-4o"})
    assert response.status_code == 200, f"Fails to update settings: {response.text}"
    logger.info(f"test_update_settings: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert (
        response.json().get("message") == "Settings updated successfully"
    ), f"Message is not correct: {response.text}"
    end_time = datetime.now()
    logger.info(f"Testing Update Settings took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


def test_get_models(client: TestClient):
    start_time = datetime.now()
    response = client.get("/settings/models")
    assert response.status_code == 200, f"Fails to get models: {response.text}"
    logger.info(f"test_get_models: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert len(response.json().get("models")) > 0, f"Models is empty: {response.text}"
    end_time = datetime.now()
    logger.info(f"Testing Get Models took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


def test_get_tags(client: TestClient):
    start_time = datetime.now()
    response = client.get("/settings/tags")
    assert response.status_code == 200, f"Fails to get tags: {response.text}"
    logger.info(f"test_get_tags: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert len(response.json().get("tags")) > 0, f"Tags is empty: {response.text}"
    end_time = datetime.now()
    logger.info(f"Testing Get Tags took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


def test_get_function(client: TestClient):
    start_time = datetime.now()
    response = client.get("/functions")
    assert response.status_code == 200, f"Fails to get functions: {response.text}"
    logger.info(f"test_get_functions: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert len(response.json()) > 0, f"Functions is empty: {response.text}"
    end_time = datetime.now()
    logger.info(f"Testing Get Functions took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


def test_health_check(client: TestClient):
    start_time = datetime.now()
    response = client.get("/health")
    assert response.status_code == 200, f"Fails to health check: {response.text}"
    logger.info(f"test_health_check: {response.json()}")
    assert response.json() is not None, f"Response is None: {response.text}"
    assert (
        response.json().get("status") == "healthy"
    ), f"Status is not healthy: {response.text}"
    end_time = datetime.now()
    logger.info(f"Testing Health Check took {end_time - start_time} seconds")
    if (end_time - start_time).total_seconds() > 1:
        raise Exception("Test takes too long")


# TODO: `test_chat`, `test_feedback` 추가
