import logging
import urllib
from types import NoneType

import pytest
from fastapi.testclient import TestClient

from .airelay import app

log = logging.getLogger("pytest")


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Get fastapi TestClient"""
    return TestClient(app)


@pytest.fixture(scope="function")
def api_base() -> str:
    """Get API base URL."""

    return "/api/v1"


@pytest.fixture(scope="function")
def api_docs() -> str:
    """Get API docs URL."""

    return "/docs"


def test_api_docs(client: TestClient, api_docs: str):
    """Quick smoke test"""

    response = client.get(f"{api_docs}")
    assert response.status_code == 200


def test_get_threads(client: TestClient, api_base):
    """Check if list of saved threads is returned and do check on data correctness."""

    response = client.get(f"{api_base}/threads")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert isinstance(rjson, list)
    assert len(rjson) > 0
    assert isinstance(rjson[0], dict)

    thread: dict = rjson[0]
    assert isinstance(thread.get("name"), str)
    assert isinstance(thread.get("thread_id"), str)
    assert isinstance(thread.get("description"), NoneType | str)


def test_get_thread_by_name(client: TestClient, api_base):
    """Check if we can retrieve saved thread by its name."""

    name = "default"
    response = client.get(f"{api_base}/threads/{name}")
    assert response.status_code == 200

    rjson: dict = response.json()
    log.info("rjson: %s", rjson)
    assert rjson.get("name") == name
    assert rjson.get("description") in (None, "default")
    assert rjson.get("thread_id", False)


def test_get_thread_by_name_missing_name(client: TestClient, api_base):
    """Check if getting non-existing name fails gracefully with 404"""

    name = "non_existing_thread"
    response = client.get(f"{api_base}/threads/{name}")
    assert response.status_code == 404


def test_list_roles(client: TestClient, api_base: str):
    """Check if roles and assistants API endpoints are reachable."""

    response = client.get(f"{api_base}/roles")
    assert response.status_code == 200

    log.info("response.json(): %s", response.json())
    messages = response.json()["msg"]
    log.info(messages)
    assert len(messages) > 0
    for role, desc in messages.items():
        log.info(role)
        log.info(desc)
        assert role
        assert len(desc["description"]) > 10


def test_show_role(client: TestClient, api_base):
    """Check if roles API endpoint contain details ["description"] key.

    :param client:
    """
    response = client.get(f"{api_base}/roles")
    assert response.status_code == 200

    log.info("response.json(): %s", response.json())
    messages = response.json()["msg"]
    log.info("messages: %s", messages)
    for role, desc in messages.items():
        log.info("\trole: %s; %s", role, desc)
        test_response = client.get(f"/api/v1/roles/{role}")
        log.info("\t\ttest_response.json()%s", test_response.json())
        assert len(test_response.json()["msg"]["description"]) > 10


def test_show_role_missing_role(client: TestClient):
    """Check if getting non-existing role fails gracefully with 404"""

    role = "non_existent_role"
    response = client.get(f"/api/v1/roles/{role}")
    assert response.status_code == 404


@pytest.mark.uses_tokens
def test_role_is_answering(client: TestClient, api_base: str):
    """Check if role can be reached."""

    prompt = urllib.parse.quote("Test question. What is 2 + 2?", safe="")
    log.info(prompt)
    response = client.post(f"{api_base}/roles/default/{prompt}")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert rjson

    for mkey in ["msg", "system"]:
        assert mkey in rjson


@pytest.mark.uses_tokens
def test_assistant_is_answering(client: TestClient, api_base: str):
    """Check if assistant can be reached."""

    prompt = urllib.parse.quote("Test question. What is 2 + 2?", safe="")
    log.info(prompt)
    response = client.post(f"{api_base}/assistant/{prompt}")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert rjson

    for mkey in ["msg", "system"]:
        assert mkey in rjson
