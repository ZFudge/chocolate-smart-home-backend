from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_get_spaces_empty(empty_test_db):
    resp = client.get("/spaces")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_spaces(populated_test_db):
    resp = client.get("/spaces")
    assert resp.status_code == 200
    expected_data = [
        {
            "id": 1,
            "name": "Main Space",
        },
        {
            "id": 2,
            "name": "Other Space",
        },
    ]
    assert resp.json() == expected_data


def test_get_space(populated_test_db):
    resp = client.get("/spaces/1")
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Main Space",
    }
    assert resp.json() == expected_data


def test_get_space(populated_test_db):
    resp = client.get("/spaces/1")
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Main Space",
    }
    assert resp.json() == expected_data


def test_create_space(empty_test_db):
    resp = client.post("/spaces/", json={"name": "New Space"})
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "New Space",
    }
    assert resp.json() == expected_data


def test_create_duplicate_space_fails(empty_test_db):
    space_name = "New Space"
    resp = client.post("/spaces/", json={"name": space_name})
    resp = client.post("/spaces/", json={"name": space_name})
    assert resp.status_code == 500
    expected_data = {
        "detail": "Key (name)=(New Space) already exists.",
    }
    assert resp.json() == expected_data


def test_update_space_name(populated_test_db):
    resp = client.put("/spaces/1", json={"name": "Updated Space Name"})
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "Updated Space Name",
    }
    assert resp.json() == expected_data


def test_update_space_name_fail(empty_test_db):
    resp = client.put("/spaces/1", json={"name": "Updated Space Name"})
    assert resp.status_code == 500
    expected_data = {
        'detail': 'Space update failed. No Space object with an id of 1 found.',
    }
    assert resp.json() == expected_data


def test_delete_space(populated_test_db):
    resp = client.delete("/spaces/1")
    assert resp.status_code == 204


def test_delete_space_fails_on_invalid_device_id(populated_test_db):
    resp = client.delete("/spaces/1234")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Space with id of 1234 - "
            "No row was found when one was required"
        )
    }


def test_delete_device_duplicate_deletion_fails(populated_test_db):
    resp = client.delete(f"/spaces/1")
    resp = client.delete(f"/spaces/1")
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": (
            "Failed to delete Space with id of 1 - "
            "No row was found when one was required"
        )
    }
