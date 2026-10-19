from app import schemas
import pytest
from jose import jwt
from app.config import settings




def test_root(client):
    res = client.get("/")
    #assert res.json().get("message") == "Welcome to the JB fastAPI Tutorial homepage!"
    assert res.status_code == 200


def test_create_user_basic(client):
    res = client.post("/users", json={"email": "testuser1@gmail.com", "password": "pwd999"})

    # pydantic will verify the right fields were returned, however will not check any of the values themselves
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "testuser1@gmail.com"
    assert res.status_code == 201

def test_create_user_all_fields(client):
    res = client.post("/users", json={"email": "testuser@gmail.com", "password": "pwd999", "short_name": "TU", "display_name": "Test User"})
    new_user = schemas.UserResponse(**res.json())
    assert new_user.email == "testuser@gmail.com"
    assert new_user.short_name == "TU"
    assert new_user.display_name == "Test User"
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