from app import schemas
import pytest
from jose import jwt
from app.config import settings
from app.oauth2 import create_access_token



def test_root(client):
    res = client.get("/")
    #assert res.json().get("message") == "Welcome to the JB fastAPI Tutorial homepage!"
    assert res.status_code == 200


def test_get_users(authorized_client, test_user, test_user2):
    res = authorized_client.get("/users")
    res.status_code == 200

def test_unauthorized_user_get_all_users(client, test_user, test_user2):
    res = client.get("/users")
    res.status_code == 401


def test_create_user_basic(client):
    res = client.post("/users", json={"email": "testuser1@gmail.com", "password": "pwd999"})

    # pydantic will verify the right fields were returned, however will not check any of the values themselves
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "testuser1@gmail.com"
    assert res.status_code == 201

def test_create_user_all_fields(client):
    data = {"email": "testuser@gmail.com", 
            "password": "pwd999", 
            "username": "tuser",
            "short_name": "TU", 
            "display_name": "Test User",
            "pc_name": "IO1234"}
    res = client.post("/users", json=data)
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "testuser@gmail.com"
    assert new_user.short_name == "TU"
    assert new_user.display_name == "Test User"
    assert new_user.username == "tuser"
    assert new_user.pc_name == "IO1234"
    assert res.status_code == 201

def test_login_user(client, test_user):
    res = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert res.status_code == 200
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"

@pytest.mark.parametrize("email, password, status_code", [
    ("wrongemail@gmail.com", "pwd999", 403), 
    ("testuser2@gmail.com", "wrongpassword", 403), 
    ("wrongemail@gmail.com", "wrongpassword", 403), 
    (None, "pwd999", 422), 
    ("testuser2@gmail.com", None, 422)
])
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code


def test_update_user(authorized_client, test_user):
    data = {"email": "changetestuser@gmail.com", 
            "username": "changeuser",
            "short_name": "CU", 
            "display_name": "Change User",
            "pc_name": "IO4444"}
    res = authorized_client.put(f"/users/{test_user["id"]}", json=data)
    updated_user = schemas.UserResponse(**res.json())

    assert res.status_code == 200
    assert updated_user.email == data["email"]
    assert updated_user.username == data["username"]
    assert updated_user.short_name == data["short_name"]
    assert updated_user.display_name == data["display_name"]
    assert updated_user.pc_name == data["pc_name"]


def test_update_other_users_profile(authorized_client, test_user, test_user2):
    data = {"email": "changetestuser@gmail.com", 
                "username": "changeuser",
                "short_name": "CU", 
                "display_name": "Change User",
                "pc_name": "IO4444"}
    res = authorized_client.put(f"/users/{test_user2["id"]}", json=data)
    assert res.status_code == 403

def test_unauthorized_user_update_profile(client, test_user):
    data = {"email": "changetestuser@gmail.com", 
                "username": "changeuser",
                "short_name": "CU", 
                "display_name": "Change User",
                "pc_name": "IO4444"}
    res = client.put(f"/users/{test_user["id"]}", json=data)
    assert res.status_code == 401

def test_unauthorized_user_delete_user(client, test_user, test_user2):
    res = client.delete(f"/users/{test_user2["id"]}")
    assert res.status_code == 401


def test_user_without_permission_delete_user(authorized_client, test_user, test_user2):
    res = authorized_client.delete(f"/users/{test_user2["id"]}")
    assert res.status_code == 404

def test_user_profile_user_delete_user(client, create_user_with_permission, test_user):
    user_id = test_user['id']
    user_profiles_user = create_user_with_permission("user_profiles", email="userProfileTestUser@gmail.com")
    token = create_access_token({"user_id": user_profiles_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/users/{user_id}")
    assert res.status_code == 204

def test_admin_user_delete_user(client, create_user_with_permission, test_user):
    user_id = test_user["id"]
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/users/{user_id}")
    assert res.status_code == 204

def test_user_deleting_themselves(client, create_user_with_permission):
    admin_user = create_user_with_permission("admin", email="adminTestUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/users/{admin_user["id"]}")
    assert res.status_code == 404


def test_admin_assigning_permission(authorized_admin_client, admin_user, test_user):
    data = {"name": "admin"}
    res = authorized_admin_client.post(f"/users/{test_user["id"]}/permissions", json=data)
    assert res.status_code == 201

def test_admin_assigning_permission_does_not_exist(authorized_admin_client, admin_user, test_user):
    data = {"name": "not_a_permission"}
    res = authorized_admin_client.post(f"/users/{test_user["id"]}/permissions", json=data)
    assert res.status_code == 400


def test_user_profile_access_assigning_permission(client, create_user_with_permission, test_user):
    # create a user with "user_profile" permission, then generate token for this user
    user_with_perm = create_user_with_permission("user_profiles", email="permuser@gmail.com")
    token = create_access_token({"user_id": user_with_perm["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    data = {"name": "admin"}
    res = client.post(f"/users/{test_user["id"]}/permissions", json=data)
    assert res.status_code == 201

def test_unauthorized_user_assigning_permissions(client, test_user, test_user2):
    data = {"name": "admin"}
    res = client.post(f"/users/{test_user2["id"]}/permissions", json=data)
    assert res.status_code == 401

def test_authorised_non_admin_assigning_permissions(authorized_client, test_user, test_user2):
    data = {"name": "admin"}
    res = authorized_client.post(f"/users/{test_user2["id"]}/permissions", json=data)
    assert res.status_code == 403


def test_unauthorized_user_delete_permission(client, create_user_with_permission):
    test_user = create_user_with_permission("read", email="readUser@gmail.com")
    res = client.delete(f"/users/{test_user['id']}/permissions/read")
    assert res.status_code == 401

def test_user_without_access_delete_permissions(authorized_client, create_user_with_permission):
    test_user = create_user_with_permission("read", email="readUser@gmail.com")
    res = authorized_client.delete(f"/users/{test_user["id"]}/permissions/read")
    assert res.status_code == 403

def test_user_profile_user_delete_permission(client, create_user_with_permission):
    test_user = create_user_with_permission("read", email="readUser@gmail.com")
    user_profile_user = create_user_with_permission("user_profiles", email="userProfileUser@gmail.com")
    token = create_access_token({"user_id": user_profile_user['id']})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    
    res = client.delete(f"/users/{test_user["id"]}/permissions/read")
    assert res.status_code == 200

def test_admin_user_delete_permission(client, create_user_with_permission):
    read_user = create_user_with_permission("read", email="readUser@gmail.com")
    admin_user = create_user_with_permission("admin", email="adminUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    res = client.delete(f"/users/{read_user["id"]}/permissions/read")
    assert res.status_code == 200

def test_delete_permission_doesnt_exist(client, create_user_with_permission):
    read_user = create_user_with_permission("read", email="readUser@gmail.com")
    admin_user = create_user_with_permission("admin", email="adminUser@gmail.com")
    token = create_access_token({"user_id": admin_user["id"]})
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    
    perm_name = "not_a_permission"
    res = client.delete(f"/users/{read_user["id"]}/permissions/{perm_name}")
    assert res.status_code == 404
    assert f"permission named '{perm_name}' does not exist" in res.json().get("detail", "").lower()

def test_delete_permission_not_assigned(authorized_admin_client, test_user):
    perm_name = "admin"
    res = authorized_admin_client.delete(f"/users/{test_user["id"]}/permissions/{perm_name}")
    assert res.status_code == 404
    assert f"does not have permission {perm_name} assigned" in res.json().get("detail", "").lower()

def test_delete_permission_user_doesnt_exist(authorized_admin_client, test_user):
    not_a_user_id = 9999
    res = authorized_admin_client.delete(f"/users/{not_a_user_id}/permissions/read")
    assert res.status_code == 404
    assert f"user with id {not_a_user_id} does not exist" in res.json().get("detail", "").lower()
