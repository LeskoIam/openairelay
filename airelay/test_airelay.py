import logging
import os
import urllib
from types import NoneType

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from .airelay import SavedThread, app, get_session

log = logging.getLogger("pytest")
load_dotenv()


@pytest.fixture(name="session")
def session_fixture() -> Session:
    """Get DB session."""

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, api_base) -> TestClient:
    """Get fastapi TestClient"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def populate_db(session: Session):
    """Fill DB with test data"""

    threads = (
        ("default", "thid_1", "Default thread"),
        ("no_description", "thid_2", None),
    )
    for thread in threads:
        default_thread = SavedThread(name=thread[0], thread_id=thread[1], description=thread[2])
        session.add(default_thread)
    session.commit()


@pytest.fixture(scope="function")
def populate_db_valid_thread_id(session: Session):
    """Fill DB with test data"""
    valid_id = os.getenv("VALID_THREAD_ID")
    if valid_id is None:
        pytest.xfail("VALID_THREAD_ID not set.")
    default_thread = SavedThread(name="default", thread_id=valid_id, description="Default thread")
    session.add(default_thread)
    session.commit()


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


def test_get_threads(client: TestClient, api_base: str, populate_db):
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


def test_get_thread_by_name(client: TestClient, api_base: str, populate_db):
    """Check if we can retrieve saved thread by its name."""

    name = "default"
    response = client.get(f"{api_base}/threads/{name}")
    assert response.status_code == 200

    rjson: dict = response.json()
    log.info("rjson: %s", rjson)
    assert rjson.get("name") == name
    assert rjson.get("description") == "Default thread"
    assert rjson.get("thread_id", False)


def test_get_thread_by_name_missing_name(client: TestClient, api_base: str, populate_db):
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
def test_assistant_is_answering(client: TestClient, api_base: str, populate_db_valid_thread_id):
    """Check if assistant can be reached."""

    prompt = urllib.parse.quote("Test question. What is 2 + 2?", safe="")
    log.info(prompt)
    response = client.post(f"{api_base}/assistant/{prompt}")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert rjson
    assert "msg" in rjson
    assert "system" in rjson


@pytest.mark.uses_tokens
def test_create_thread(client: TestClient, api_base):
    """Check if new thread can be created."""

    response = client.post(
        f"{api_base}/threads/", json={"name": "Deadpond", "thread_id": "Dive Wilson", "description": None}
    )
    assert response.status_code == 200

    data = response.json()
    log.info("data: %s", data)

    assert data["name"] == "Deadpond"
    assert data["description"] is None
