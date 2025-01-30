from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_get_tags_empty(empty_test_db):
    resp = client.get("/tags")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_tags(populated_test_db):
    resp = client.get("/tags")
    assert resp.status_code == 200
    expected_data = [
        {
            "id": 1,
            "name": "Main Tag",
        },
        {
            "id": 2,
            "name": "Other Tag",
        },
    ]
    assert resp.json() == expected_data


def test_get_tag_does_not_exist(empty_test_db):
    resp = client.get("/tags/1")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "No Tag with an id of 1 found."}


def test_get_tag(populated_test_db):
    resp = client.get("/tags/1")
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Main Tag",
    }
    assert resp.json() == expected_data


def test_create_tag(empty_test_db):
    resp = client.post("/tags/", json={"name": "New Tag"})
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "New Tag",
    }
    assert resp.json() == expected_data


def test_create_duplicate_tag_fails(empty_test_db):
    tag_name = "New Tag"
    resp = client.post("/tags/", json={"name": tag_name})
    resp = client.post("/tags/", json={"name": tag_name})
    assert resp.status_code == 500
    expected_data = {
        "detail": "Key (name)=(New Tag) already exists.",
    }
    assert resp.json() == expected_data


def test_update_tag_name(populated_test_db):
    resp = client.put("/tags/1", json={"name": "Updated Tag Name"})
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Updated Tag Name",
    }
    assert resp.json() == expected_data


def test_update_tag_name_fail(empty_test_db):
    resp = client.put("/tags/1", json={"name": "Updated Tag Name"})
    assert resp.status_code == 500
    expected_data = {
        "detail": "Tag update failed. No Tag object with an id of 1 found.",
    }
    assert resp.json() == expected_data


def test_delete_tag(populated_test_db):
    resp = client.delete("/tags/1")
    assert resp.status_code == 204


def test_delete_tag_fails_on_invalid_device_id(populated_test_db):
    resp = client.delete("/tags/1234")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Tag with id of 1234 - "
            "No row was found when one was required"
        )
    }


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    resp = client.delete("/tags/1")
    resp = client.delete("/tags/1")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Tag with id of 1 - "
            "No row was found when one was required"
        )
    }
