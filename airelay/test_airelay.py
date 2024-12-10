import logging
import urllib

import pytest
from fastapi.testclient import TestClient

from .airelay import app

log = logging.getLogger("pytest")


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Get fastapi TestClient"""
    return TestClient(app)


@pytest.mark.parametrize("ra", ["roles", "assistants"])
def test_list_roles_assistants(client: TestClient, ra: str):
    """Test if roles and assistants API endpoints are reachable.

    :param client:
    :param ra:
    """
    response = client.get(f"/api/v1/{ra}")

    assert response.status_code == 200
    log.info(response.json())
    messages = response.json()["msg"]
    log.info(messages)
    assert len(messages) > 0
    for role, desc in messages.items():
        log.info(role)
        log.info(desc)
        assert role
        assert len(desc["description"]) > 10


@pytest.mark.parametrize("ra", ["roles", "assistants"])
def test_show_roles_assistants(client: TestClient, ra: str):
    """Test if roles and assistants API endpoints contain details ["description"] key.

    :param client:
    :param ra:
    """
    response = client.get(f"/api/v1/{ra}")

    assert response.status_code == 200
    log.info("response.json(): %s", response.json())
    messages = response.json()["msg"]
    log.info("messages: %s", messages)
    for role, desc in messages.items():
        log.info("\trole: %s", role)
        log.info("\tdesc: %s", desc)
        test_response = client.get(f"/api/v1/{ra}/{role}")
        log.info("\t\ttest_response.json()%s", test_response.json())
        assert len(test_response.json()["msg"]["description"]) > 10


@pytest.mark.parametrize("role", ["spock", "bugsbunny", "default"])
def test_roles(client: TestClient, role: str):
    """Check if all predefined roles can be reached."""

    prompt = urllib.parse.quote("Test question. What is 2 + 2?", safe="")
    log.info(prompt)
    response = client.post(f"/api/v1/roles/{role}/{prompt}")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert rjson

    for mkey in ["msg", "system"]:
        assert mkey in rjson
