from fastapi.testclient import TestClient

from app import app, items_db

client = TestClient(app)


def setup_function() -> None:
    items_db.clear()
    # Reset id counter and hive singleton
    import app as app_module

    app_module.next_id = 1
    app_module.hive_client = None


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_item() -> None:
    created = client.post("/items", json={"name": "Book", "description": "Python"})
    assert created.status_code == 200
    created_data = created.json()
    assert created_data["id"] == 1

    fetched = client.get("/items/1")
    assert fetched.status_code == 200
    assert fetched.json() == created_data


def test_list_items() -> None:
    client.post("/items", json={"name": "A", "description": "a"})
    client.post("/items", json={"name": "B", "description": "b"})

    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "A"
    assert data[1]["name"] == "B"


def test_update_item() -> None:
    client.post("/items", json={"name": "Old", "description": "old"})

    response = client.put("/items/1", json={"name": "New", "description": "new"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "New", "description": "new"}


def test_update_item_not_found() -> None:
    response = client.put("/items/999", json={"name": "X", "description": "Y"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_item() -> None:
    client.post("/items", json={"name": "Temp", "description": "tmp"})

    delete_resp = client.delete("/items/1")
    assert delete_resp.status_code == 200
    assert delete_resp.json() == {"message": "Item deleted"}

    get_resp = client.get("/items/1")
    assert get_resp.status_code == 404


def test_delete_item_not_found() -> None:
    response = client.delete("/items/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_hive_query_success(monkeypatch) -> None:
    class FakeHive:
        def get_info(self, _sql: str):
            return [(1, "ok")]

    import app as app_module

    monkeypatch.setattr(app_module, "get_hive_client", lambda: FakeHive())

    response = client.post("/hive/query", json={"sql": "select 1"})
    assert response.status_code == 200
    assert response.json() == {"rows": [[1, "ok"]]}


def test_hive_query_failure(monkeypatch) -> None:
    class FakeHive:
        def get_info(self, _sql: str):
            raise RuntimeError("boom")

    import app as app_module

    monkeypatch.setattr(app_module, "get_hive_client", lambda: FakeHive())

    response = client.post("/hive/query", json={"sql": "select 1"})
    assert response.status_code == 500
    assert "Hive query failed" in response.json()["detail"]
