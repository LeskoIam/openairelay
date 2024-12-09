import logging
import urllib

import pytest
from fastapi.testclient import TestClient

from .airelay import app

log = logging.getLogger("pytest")


@pytest.fixture(scope="function")
def client() -> TestClient:
    """Get fastapi TestClient"""
    return TestClient(app)


@pytest.mark.parametrize("role", ["Spock", "BugsBunny", "default"])
def test_roles(client: TestClient, role: str):
    """Check if all predefined roles can be reached."""

    prompt = urllib.parse.quote("Test question. What is 2 + 2?", safe="")
    log.info(prompt)
    response = client.post(f"/api/v1/roles/predefined/{role}/{prompt}")
    assert response.status_code == 200

    rjson = response.json()
    log.info(rjson)
    assert rjson

    for mkey in ["msg", "system"]:
        assert mkey in rjson
