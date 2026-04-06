from unittest.mock import patch

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
    assert resp.json() == [
        {
            "id": 1,
            "name": "Main Tag",
        },
        {
            "id": 2,
            "name": "Other Tag",
        },
        {
            "id": 3,
            "name": "Third Tag",
        },
    ]


def test_raises_exception_on_get_tags(populated_test_db):
    with patch(
        "src.routers.tags.crud.get_tags", side_effect=Exception("Test exception")
    ):
        resp = client.get("/tags")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to get tags.",
        }


def test_get_tag_does_not_exist(empty_test_db):
    resp = client.get("/tags/1")
    assert resp.status_code == 200
    assert resp.json() is None


def test_get_tag(populated_test_db):
    resp = client.get("/tags/1")
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "name": "Main Tag",
    }


def test_raises_exception_on_get_tag_by_id(populated_test_db):
    with patch(
        "src.routers.tags.crud.get_tag_by_id", side_effect=Exception("Test exception")
    ):
        resp = client.get("/tags/1")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to get tag by id 1.",
        }


def test_create_tag(empty_test_db):
    resp = client.post("/tags/", json={"name": "New Tag"})
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "name": "New Tag",
    }


def test_create_duplicate_tag_fails(empty_test_db):
    resp = client.post("/tags/", json={"name": "New Tag"})
    resp = client.post("/tags/", json={"name": "New Tag"})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": 'Tag with name "New Tag" already exists.',
    }


def test_raises_exception_on_create_tag(populated_test_db):
    with patch(
        "src.routers.tags.crud.create_tag", side_effect=Exception("Test exception")
    ):
        resp = client.post("/tags/", json={"name": "New Tag"})
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": 'Failed to create tag with name of "New Tag".',
        }


def test_raises_exception_on_none_returned_create_tag(populated_test_db):
    with patch("src.routers.tags.crud.create_tag", return_value=None):
        resp = client.post("/tags/", json={"name": "New Tag"})
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": 'Failed to create tag with name of "New Tag".',
        }


def test_delete_tag(populated_test_db):
    resp = client.delete("/tags/1")
    assert resp.status_code == 204
    assert client.get("/tags/1").json() is None


def test_delete_tag_fails_on_invalid_tag_id(populated_test_db):
    resp = client.delete("/tags/1234")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Tag with id of 1234. "
            "No Tag object with an id of 1234 found."
        )
    }


def test_delete_tag_duplicate_deletion_fails(populated_test_db):
    resp = client.delete("/tags/1")
    resp = client.delete("/tags/1")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Tag with id of 1. " "No Tag object with an id of 1 found."
        )
    }


def test_raises_exception_on_delete_tag(populated_test_db):
    with patch(
        "src.routers.tags.crud.delete_tag", side_effect=Exception("Test exception")
    ):
        resp = client.delete("/tags/1")
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to delete tag of id 1.",
        }


def test_patch_tag_name_request(populated_test_db):
    resp = client.patch("/tags", json={"id": 1, "name": "Updated Tag Name"})
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 1,
        "name": "Updated Tag Name",
    }
    assert resp.json() == client.get("/tags/1").json()


def test_patch_tag_does_not_exist(empty_test_db):
    resp = client.patch("/tags", json={"id": 1, "name": "Updated Tag Name"})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Tag update failed. No Tag object with an id of 1 found.",
    }


def test_raises_exception_on_patch_tag(empty_test_db):
    with patch(
        "src.routers.tags.crud.patch_tag", side_effect=Exception("Test exception")
    ):
        resp = client.patch("/tags", json={"id": 1, "name": "Updated Tag Name"})
        assert resp.status_code == 500
        assert resp.json() == {
            "detail": "Failed to patch tag of id 1.",
        }
