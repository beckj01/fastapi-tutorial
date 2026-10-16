from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
import pytest

# override to use a testing database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# scope allows the fixute to re-run at different times, hence either preserve or create new database between testing
#    function - re-runs the fixture & re-creates the database between each test function
#    module - re-runs the fixture & between each testing function
#    sesssion - only runs the fixture once for the entire testing session
# function is default & best practice so that each test is independent & a test won't fail because a previous test failed.)
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session): # this will cause the session fixture to run before the client fixture
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # overrides the dependency so that a new testing database is used rather than the development db
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    user_data = {"email": "testuser1@gmail.com", "password": "pwd999"}
    res = client.post("/users", json=user_data)
    
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user

@pytest.fixture()
def test_user2(client):
    user_data = {"email": "testuser2@gmail.com", "password": "pwd999"}
    res = client.post("/users", json=user_data)
    
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture()
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers, 
        "Authorization": f"Bearer {token}"
    }
    return client



@pytest.fixture()
def test_posts(test_user, test_user2, session):
    post_data = [
        {"title": "First Post Title",
         "content": "First Post Content", 
         "owner_id": test_user["id"]}, 
        {"title": "Second Post Title",
        "content": "Second Post Content", 
        "owner_id": test_user["id"]}, 
        {"title": "Third Post Title",
        "content": "Third Post Content", 
        "owner_id": test_user["id"]}, 
        {"title": "Other Users Title", 
         "content": "Another Users Content", 
         "owner_id": test_user2["id"]}
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, post_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()
    session.query(models.Post).all()
    return posts