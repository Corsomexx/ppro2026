from fastapi.testclient import TestClient

def test_api_list_equipment_empty(client: TestClient):
    response = client.get("/api/equipment")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_create_and_get_item(client: TestClient):
    payload = {
        "inventory_number": "BOAT-100",
        "name": "Kanoe Pálava",
        "category": "Kanoe a rafty",
        "size": "2-místná",
        "year_of_purchase": 2023,
        "daily_rate": 450.0,
        "condition": "Nové",
        "status": "Dostupné",
        "note": "Nafukovací kanoe"
    }

    create_res = client.post("/api/equipment", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["id"] is not None
    assert created_data["inventory_number"] == "BOAT-100"

    item_id = created_data["id"]
    get_res = client.get(f"/api/equipment/{item_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Kanoe Pálava"

def test_api_duplicate_inventory_number_conflict(client: TestClient):
    payload = {
        "inventory_number": "DUP-001",
        "name": "Boty Dalbello",
        "category": "Lyžařské boty",
        "size": "42 EU",
        "year_of_purchase": 2023,
        "daily_rate": 150.0
    }

    res1 = client.post("/api/equipment", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/equipment", json=payload)
    assert res2.status_code == 409
    assert "již obsazeno" in res2.json()["detail"]

def test_api_service_workflow(client: TestClient):
    # 1. Vytvoření
    payload = {
        "inventory_number": "TEST-FLOW",
        "name": "Testovací lyže",
        "category": "Sjezdové lyže",
        "size": "160 cm",
        "year_of_purchase": 2024,
        "daily_rate": 300.0
    }
    create_res = client.post("/api/equipment", json=payload)
    item_id = create_res.json()["id"]

    # 2. Odeslání do servisu
    serv_res = client.post(f"/api/equipment/{item_id}/send-to-service", json={
        "reason_or_work": "Broušení hran",
        "condition_after": "Běžné opotřebení"
    })
    assert serv_res.status_code == 200
    assert serv_res.json()["status"] == "V servisu"

    # 3. Pokus o zapůjčení přímo ze servisu (musí selhat 400 Bad Request)
    patch_res = client.patch(f"/api/equipment/{item_id}/status", json={
        "status": "Vypůjčeno"
    })
    assert patch_res.status_code == 400
    assert "v servisu" in patch_res.json()["detail"].lower()

    # 4. Návrat ze servisu
    return_res = client.post(f"/api/equipment/{item_id}/return-from-service", json={
        "reason_or_work": "Broušení dokončeno",
        "condition_after": "Nové"
    })
    assert return_res.status_code == 200
    assert return_res.json()["status"] == "Dostupné"
