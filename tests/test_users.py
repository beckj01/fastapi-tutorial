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


def test_admin_assigning_permission(authorized_admin_client, admin_user, test_user):
    data = {"name": "admin"}
    res = authorized_admin_client.post(f"/users/{test_user["id"]}/permissions", json=data)
    assert res.status_code == 201

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
    assert res.status_code == 404