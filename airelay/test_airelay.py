import logging

import pytest
from fastapi.testclient import TestClient

from .airelay import app

log = logging.getLogger("pytest")


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.mark.parametrize("role", ["Spock", "BugsBunny", "default"])
def test_roles(client, role):
    response = client.post(f"/api/v1/roles/predefined/{role}/Why")
    assert response.status_code == 200
    rjson = response.json()
    assert rjson

    for mkey in ["msg", "system"]:
        assert mkey in rjson
