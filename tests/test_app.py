import pytest

from app.main import add, app, multiply


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_add():
    assert add(2, 3) == 5


def test_multiply():
    assert multiply(4, 5) == 20


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_health(client):
    response = client.get("/health")
    assert response.get_json() == {"status": "ok"}


def test_add_endpoint(client):
    response = client.get("/add?a=2&b=3")
    assert response.get_json() == {"result": 5.0}


def test_add_endpoint_bad_input(client):
    response = client.get("/add?a=x&b=3")
    assert response.status_code == 400
