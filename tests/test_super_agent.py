from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_keyword_columns_and_listening_feed() -> None:
    col = client.post("/columns", json={"name": "Sertanejo"})
    assert col.status_code == 200

    col2 = client.post("/columns", json={"name": "Mari Fernandes"})
    assert col2.status_code == 200

    client.post(
        "/mentions",
        json={"text": "Novo hit de Sertanejo, música incrível!", "source": "x"},
    )
    client.post(
        "/mentions",
        json={"text": "Mari Fernandes lançou show top", "source": "instagram"},
    )

    feed = client.get("/listening/Sertanejo")
    assert feed.status_code == 200
    data = feed.json()

    assert data["column"] == "Sertanejo"
    assert data["volume"] >= 1
    assert "mentions" in data
    assert data["sentiment"]["positivo"] >= 1


def test_duplicate_column_returns_conflict() -> None:
    first = client.post("/columns", json={"name": "Forró"})
    assert first.status_code == 200

    second = client.post("/columns", json={"name": "forró"})
    assert second.status_code == 409
