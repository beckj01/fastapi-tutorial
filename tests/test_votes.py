import pytest
from app import schemas, models


@pytest.fixture()
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id = test_posts[3].id, user_id = test_user["id"])
    session.add(new_vote)
    session.commit()

def test_vote_on_post(authorized_client, test_posts):
    data = {"post_id": test_posts[0].id,
            "direction": 1}
    res = authorized_client.post("/vote", json=data)
    assert res.status_code == 201

def test_vote_twice_post(authorized_client, test_posts, test_vote):
    data = {"post_id": test_posts[3].id,
            "direction": 1}
    res = authorized_client.post("/vote", json=data)
    assert res.status_code == 409

def test_delete_vote(authorized_client, test_posts, test_vote):
    data = {"post_id": test_posts[3].id,
            "direction": 0}
    res = authorized_client.post("/vote", json=data)
    assert res.status_code == 201

def test_delete_vote_not_exist(authorized_client, test_posts, test_vote):
    data = {"post_id": test_posts[0].id, 
            "direction": 0}
    res = authorized_client.post("/vote", json=data)
    assert res.status_code == 404 

def test_vote_post_not_exist(authorized_client, test_posts):
    data = {"post_id": 9999, 
            "direction": 1}
    res = authorized_client.post("/vote", json=data)
    assert res.status_code == 404

def test_vote_unauthorized_user_cannot_vote(client, test_posts):
    data = {"post_id": test_posts[0].id, 
            "direction": 1}
    res = client.post("/vote", json=data)
    assert res.status_code == 401