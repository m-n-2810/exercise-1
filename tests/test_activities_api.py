import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(app_module.activities))
    return TestClient(app_module.app)


def test_get_activities_returns_available_activities(client: TestClient) -> None:
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_adds_participant(client: TestClient) -> None:
    email = "new-student@example.com"

    response = client.post("/activities/Basketball Team/signup", params={"email": email})

    assert response.status_code == 200
    assert email in client.get("/activities").json()["Basketball Team"]["participants"]


def test_signup_rejects_duplicate_participant(client: TestClient) -> None:
    email = "new-student@example.com"
    client.post("/activities/Basketball Team/signup", params={"email": email})

    response = client.post("/activities/Basketball Team/signup", params={"email": email})

    assert response.status_code == 400
    assert client.get("/activities").json()["Basketball Team"]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client: TestClient) -> None:
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@example.com"})

    assert response.status_code == 404


def test_unregister_removes_participant(client: TestClient) -> None:
    email = "new-student@example.com"
    client.post("/activities/Basketball Team/signup", params={"email": email})

    response = client.delete("/activities/Basketball Team/signup", params={"email": email})

    assert response.status_code == 200
    assert email not in client.get("/activities").json()["Basketball Team"]["participants"]


def test_unregister_rejects_unknown_activity(client: TestClient) -> None:
    response = client.delete("/activities/Unknown Club/signup", params={"email": "student@example.com"})

    assert response.status_code == 404


def test_unregister_rejects_unregistered_participant(client: TestClient) -> None:
    response = client.delete(
        "/activities/Basketball Team/signup",
        params={"email": "not-registered@example.com"},
    )

    assert response.status_code == 404