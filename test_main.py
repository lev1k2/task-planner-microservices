from fastapi.testclient import TestClient
from task_service import app

client = TestClient(app)

def test_create_task_endpoint():
    response = client.post(
        "/api/tasks",
        json={"title": "Лабораторная работа", "description": "Сдать вовремя"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Лабораторная работа"
    assert data["status"] == "new"
    assert "id" in data
    assert "created_at" in data
