import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample():
    # First holdout row displayed in code.ipynb.
    return {
        "ALLSKY_SFC_SW_DWN": 0.0,
        "T2M": 27.7,
        "T2MDEW": 19.38,
        "RH2M": 60.49,
        "WS10M": 1.93,
        "Hour": 20,
        "Month": 4,
        "DayOfYear": 94,
    }


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"name": "SOLRIZ Solar Generation API", "docs": "/docs"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_swagger(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
    assert "post" in client.get("/openapi.json").json()["paths"]["/predict"]


def test_successful_prediction(client, sample):
    # The JSON key order is independent of the model's feature order.
    response = client.post("/predict", json=dict(reversed(list(sample.items()))))
    assert response.status_code == 200
    assert isinstance(response.json()["predicted_generation"], float)


def test_notebook_sample_prediction(client, sample):
    response = client.post("/predict", json=sample)
    assert response.status_code == 200
    assert response.json()["predicted_generation"] == pytest.approx(178.7476348876953, abs=1e-6, rel=0)


def test_missing_field(client, sample):
    del sample["T2M"]
    response = client.post("/predict", json=sample)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "T2M"]


@pytest.mark.parametrize(("field", "value"), [
    ("T2M", "27.7"),
    ("Hour", True),
    ("Month", 4.5),
    ("WS10M", None),
])
def test_invalid_types(client, sample, field, value):
    sample[field] = value
    assert client.post("/predict", json=sample).status_code == 422


@pytest.mark.parametrize(("field", "value"), [
    ("ALLSKY_SFC_SW_DWN", -1),
    ("T2MDEW", 1e100),
    ("RH2M", 101),
    ("WS10M", -1),
    ("Hour", 24),
    ("Month", 0),
    ("DayOfYear", 367),
    ("unexpected", 1),
])
def test_feature_validation(client, sample, field, value):
    sample[field] = value
    assert client.post("/predict", json=sample).status_code == 422


@pytest.mark.parametrize("literal", ["NaN", "1e400"])
def test_non_finite_input(client, sample, literal):
    import json

    body = json.dumps(sample).replace('"T2M": 27.7', f'"T2M": {literal}')
    response = client.post("/predict", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "T2M"]
