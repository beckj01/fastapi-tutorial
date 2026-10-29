import pytest
from datetime import date
from app import schemas
from app.oauth2 import create_access_token


def test_get_qty(authorized_client, test_user, test_qtys):
    res = authorized_client.get("/qty")
    assert res.status_code == 200

def test_unauthorized_get_qty(client, test_user, test_qtys):
    res = client.get("/qty")
    assert res.status_code == 401

def test_get_qty_single(authorized_client, test_user, test_qtys):
    res = authorized_client.get(f"/qty/{test_qtys[0].id}")
    qty = schemas.QtyResponse(**res.json())
    
    assert res.status_code == 200
    assert qty.name == test_qtys[0].name
    assert qty.UoM == test_qtys[0].UoM
    assert qty.area == test_qtys[0].area
    assert qty.owner_id == test_user['id']
    
    assert qty.entries[0].we_date == test_qtys[0].entries[0].we_date
    assert qty.entries[0].cumulative_plan == test_qtys[0].entries[0].cumulative_plan
    assert qty.entries[0].period_plan == test_qtys[0].entries[0].period_plan
    assert qty.entries[0].cumulative_actual == test_qtys[0].entries[0].cumulative_actual
    assert qty.entries[0].period_actual == test_qtys[0].entries[0].period_actual
    assert qty.entries[0].cumulative_forecast == test_qtys[0].entries[0].cumulative_forecast
    assert qty.entries[0].period_forecast == test_qtys[0].entries[0].period_forecast
    
def test_unauthorized_get_qty_singe(client, test_user, test_qtys):
    res = client.get(f"/qty/{test_qtys[0].id}")
    assert res.status_code == 401

def test_unauthorised_user_create_qty(client, test_user):
    res = client.post("/qty", json={"name": "Dynamic Testing", "UoM": "test cases", "area": "COM"})
    assert res.status_code == 401

def test_user_without_permission_create_qty(client, create_user_with_permission):
    new_user = create_user_with_permission("read", email="qtytestuser@gmail.com")
    token = create_access_token({"user_id": new_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.post("/qty", json={"name": "Dynamic Testing", "UoM": "test cases", "area": "COM"})
    assert res.status_code == 404

def test_qty_user_create_qty(client, create_user_with_permission):
    new_user = create_user_with_permission("qty", email="qtyTestUser@gmail.com")
    token = create_access_token({"user_id": new_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "Dynamic Testing", "UoM": "test cases", "area": "COM"}
    res = client.post("/qty", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 201
    assert qty.name == data["name"]
    assert qty.UoM == data["UoM"]
    assert qty.area == data["area"]

@pytest.mark.parametrize("qty_name, uom, area", [
    ("Dynamic Testing", "test cases", "COM"), 
    ("Integration Testing", "test cases", "COM"), 
    ("Ops Readiness Testing", "test cases", "ORT")
])
def test_admin_user_create_qty_req_fields(client, create_user_with_permission, qty_name, uom, area):
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": qty_name, "UoM": uom, "area": area}
    res = client.post("/qty", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 201
    assert qty.name == data["name"]
    assert qty.UoM == data["UoM"]
    assert qty.area == data["area"]

def test_admin_user_create_qty_w_owner_id(client, create_user_with_permission):
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "Dynamic Testing", "UoM": "test cases", "area": "COM", "owner_id": admin_user["id"]}
    res = client.post("/qty", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 201
    assert qty.name == data["name"]
    assert qty.owner_id == data["owner_id"]

def test_admin_user_create_qty_w_parent_qty(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "Dynamic Testing", "UoM": "test cases", "area": "COM", 
            "owner_id": admin_user["id"], "parent_id": qty_id}
    res = client.post("/qty", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 201
    assert qty.name == data["name"]
    assert qty.UoM == data["UoM"]
    assert qty.area == data["area"]
    assert qty.owner_id == data["owner_id"]
    assert qty.parent_id == data["parent_id"]

def test_unauthorized_user_update_qty(client, test_qtys):
    data = {"name": "Regression Testing", "UoM": "test cases", "area": "MIG"}
    res = client.put(f"/qty/{test_qtys[0].id}", json=data)
    assert res.status_code == 401

def test_user_without_permission_update_qty(authorized_client, test_qtys):
    data = {"name": "Regression Testing", "UoM": "test cases", "area": "MIG"}
    res = authorized_client.put(f"/qty/{test_qtys[0].id}", json=data)
    assert res.status_code == 404
    
def test_qty_user_update_qty(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    qty_user = create_user_with_permission("qty", email="qtyTestUser@gmail.com")
    token = create_access_token({"user_id": qty_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "Regression Testing", "UoM": "test cases", "area": "COM"}
    res = client.put(f"/qty/{qty_id}", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 200
    assert qty.name == data["name"]
    assert qty.UoM == data["UoM"]
    assert qty.area == data ["area"]

def test_admin_user_update_qty(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    parent_qty_id = test_qtys[1].id
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "Regression Testing", "UoM": "test cases", "area": "COM",
            "owner_id": admin_user["id"], "parent_id": parent_qty_id}
    res = client.put(f"/qty/{qty_id}", json=data)
    qty = schemas.QtyResponse(**res.json())
    assert res.status_code == 200
    assert qty.name == data["name"]
    assert qty.UoM == data["UoM"]
    assert qty.area == data["area"]
    assert qty.owner_id == data["owner_id"]
    assert qty.parent_id == data["parent_id"]

def test_unauthorized_user_delete_qty(client, test_qtys):
    res = client.delete(f"/qty/{test_qtys[0].id}")
    assert res.status_code == 401

def test_user_without_permission_delete_qty(authorized_client, test_qtys):
    res = authorized_client.delete(f"/qty/{test_qtys[0].id}")
    assert res.status_code == 404

def test_qty_user_delete_qty(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    qty_user = create_user_with_permission("qty", email="qtyTestUser@gmail.com")
    token = create_access_token({"user_id": qty_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/qty/{qty_id}")
    assert res.status_code == 204

def test_admin_user_delete_qty(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/qty/{qty_id}")
    assert res.status_code == 204



# ------- the the quantity entry time dependent records -------------------------
def test_unauthorized_user_create_qty_entry(client, test_qtys):
    data = {"we_date": "2026-10-25", "cumulative_plan": 15, "period_plan": 5}
    res = client.post(f"/qty/{test_qtys[0].id}/entries", json=data)
    assert res.status_code == 401

def test_user_without_permission_create_qty_entry(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    read_user = create_user_with_permission("read", email="readUser@gmail.com")
    token = create_access_token({"user_id": read_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"we_date": "2026-10-25", "cumulative_plan": 15, "period_plan": 5}
    res = client.post(f"/qty/{qty_id}/entries", json=data)
    assert res.status_code == 403

def test_qty_user_create_qty_entry(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    qty_user = create_user_with_permission("qty", email="qtyUser@gmail.com")
    token = create_access_token({"user_id": qty_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"we_date": "2026-10-25", "cumulative_plan": 15, "period_plan": 5}
    res = client.post(f"/qty/{qty_id}/entries", json=data)
    qty_entry = schemas.QtyEntryResponse(**res.json())
    assert res.status_code == 201
    assert qty_entry.we_date.date() == date.fromisoformat(data["we_date"])
    assert qty_entry.cumulative_plan == data["cumulative_plan"]
    assert qty_entry.period_plan == data["period_plan"]
    assert qty_entry.cumulative_actual == 0
    assert qty_entry.period_actual == 0
    assert qty_entry.cumulative_forecast == 0
    assert qty_entry.period_forecast == 0

def test_admin_create_qty_entry(client, create_user_with_permission, test_qtys):
    qty_id = test_qtys[0].id
    admin_user = create_user_with_permission("admin", email="adminUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"we_date": "2026-10-25", "cumulative_plan": 15, "period_plan": 5, "cumulative_actual": 12,
            "period_actual": 4, "cumulative_forecast": 13, "period_forecast": 5}
    res = client.post(f"/qty/{qty_id}/entries", json=data)
    qty_entry = schemas.QtyEntryResponse(**res.json())
    assert res.status_code == 201
    assert qty_entry.we_date.date() == date.fromisoformat(data["we_date"])
    assert qty_entry.cumulative_plan == data["cumulative_plan"]
    assert qty_entry.period_plan == data["period_plan"]
    assert qty_entry.cumulative_actual == data["cumulative_actual"]
    assert qty_entry.period_actual == data["period_actual"]
    assert qty_entry.cumulative_forecast == data["cumulative_forecast"]
    assert qty_entry.period_forecast == data["period_forecast"]

def test_create_qty_entry_qty_not_exist(authorized_admin_client, test_qtys):
    data = {"we_date": "2026-10-25", "cumulative_plan": 15, "period_plan": 5}
    not_qty_id = 9999
    res = authorized_admin_client.post(f"/qty/{not_qty_id}/entries", json=data)
    assert res.status_code == 404
    assert f"quantity with id {not_qty_id} does not exist" in res.json().get("detail", "").lower()

def test_unauthorized_user_update_qty_entry(client, test_qtys):
    data = {"we_date": "2026-10-18", "cumulative_plan": 5, "cumulative_actual": 2}
    res = client.put(f"/qty/entries/{test_qtys[0].entries[0].id}", json=data)
    assert res.status_code == 401

def test_user_without_permission_update_qty_entry(authorized_client, test_qtys):
    data = {"we_date": "2026-10-18", "cumulative_plan": 5, "cumulative_actual": 2}
    res = authorized_client.put(f"/qty/entries/{test_qtys[0].entries[0].id}", json=data)
    assert res.status_code == 403
    assert f"you do not have the required 'qty' premission" in res.json().get("detail", "").lower()
    
def test_user_profile_update_qty_entry(client, create_user_with_permission, test_qtys):
    entry_id = test_qtys[0].entries[0].id
    qty_user = create_user_with_permission("qty", email="qtyUser@gmail.com")
    token = create_access_token({"user_id": qty_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"we_date": "2026-10-18", "cumulative_plan": 5, "cumulative_actual": 2}
    res = client.put(f"/qty/entries/{entry_id}", json=data)
    qty_entry = schemas.QtyEntryResponse(**res.json())
    assert res.status_code == 200
    assert qty_entry.we_date.date() == date.fromisoformat(data["we_date"])
    assert qty_entry.cumulative_plan == data["cumulative_plan"]
    assert qty_entry.cumulative_actual == data["cumulative_actual"]
    assert qty_entry.period_plan == 0
    assert qty_entry.period_actual == 0

def test_admin_update_qty_entry(authorized_admin_client, test_qtys):
    data = {"we_date": "2026-10-18", "cumulative_plan": 5, "cumulative_actual": 2, 
            "period_plan": 2, "period_actual": 1}
    res = authorized_admin_client.put(f"/qty/entries/{test_qtys[0].entries[0].id}", json=data)
    qty_entry = schemas.QtyEntryResponse(**res.json())
    assert res.status_code == 200
    assert qty_entry.we_date.date() == date.fromisoformat(data["we_date"])
    assert qty_entry.cumulative_plan == data["cumulative_plan"]
    assert qty_entry.cumulative_actual == data["cumulative_actual"]
    assert qty_entry.period_plan == data["period_plan"]
    assert qty_entry.period_actual == data["period_actual"]
    assert qty_entry.cumulative_forecast == 0
    assert qty_entry.period_forecast == 0

def test_update_qty_entry_qty_not_exist(authorized_admin_client, test_qtys):
    data = {"we_date": "2026-10-18", "cumulative_plan": 5, "cumulative_actual": 2}
    not_entry_id = 9999
    res = authorized_admin_client.put(f"/qty/entries/{not_entry_id}", json=data)
    assert res.status_code == 404
    assert f"quantity with entry {not_entry_id} not found" in res.json().get("detail", "").lower()


def test_unauthorized_user_delete_qty_entry(client, test_qtys):
    res = client.delete(f"/qty/entries/{test_qtys[0].entries[0].id}")
    assert res.status_code == 401

def test_user_without_permission_delete_qty_entry(authorized_client, test_qtys):
    res = authorized_client.delete(f"/qty/entries/{test_qtys[0].entries[0].id}")
    assert res.status_code == 403
    assert "you do not have the required 'qty' permission" in res.json().get("detail", "").lower()

def test_user_profile_delete_qty_entry(client, create_user_with_permission, test_qtys):
    entry_id = test_qtys[0].entries[0].id
    qty_user = create_user_with_permission("qty", email="qtyUser@gmail.com")
    token = create_access_token({"user_id": qty_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    
    res = client.delete(f"/qty/entries/{entry_id}")
    assert res.status_code == 204

def test_admin_delete_qty_entry(authorized_admin_client, test_qtys):
    res = authorized_admin_client.delete(f"/qty/entries/{test_qtys[0].entries[0].id}")
    assert res.status_code == 204

def test_delete_qty_entry_qty_not_exist(authorized_admin_client, test_qtys):
    not_entry_id = 9999
    res = authorized_admin_client.delete(f"/qty/entries/{not_entry_id}")
    assert res.status_code == 404
    assert f"quantity entry with id {not_entry_id} not found" in res.json().get("detail", "").lower()




