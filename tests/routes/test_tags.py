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
        {
            "id": 3,
            "name": "Third Tag",
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


def test_put_device_tags(populated_test_db):
    resp = client.put("/device/123/tags", json={"ids": [1, 2, 3]})
    assert resp.status_code == 200

    expected_data = {
        "id": 1,
        "name": "Test Device Name 1",
        "tags": [
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
        ],
        "device_type": {
            "id": 1,
            "name": "TEST_DEVICE_TYPE_NAME_1",
        },
        "mqtt_id": 123,
        "reboots": 0,
        "remote_name": "Remote Name 1 - 1",
    }
    assert resp.json() == expected_data


def test_put_device_tags_no_tags_none_ids_value(populated_test_db):
    resp = client.put("/device/123/tags", json={"ids": None})
    assert resp.status_code == 200

    expected_data = {
        "id": 1,
        "name": "Test Device Name 1",
        "tags": [],
        "device_type": {
            "id": 1,
            "name": "TEST_DEVICE_TYPE_NAME_1",
        },
        "mqtt_id": 123,
        "reboots": 0,
        "remote_name": "Remote Name 1 - 1",
    }
    assert resp.json() == expected_data


def test_put_device_tags_no_tags_empty_ids_value(populated_test_db):
    resp = client.put("/device/123/tags", json={"ids": []})
    assert resp.status_code == 200

    expected_data = {
        "id": 1,
        "name": "Test Device Name 1",
        "tags": [],
        "device_type": {
            "id": 1,
            "name": "TEST_DEVICE_TYPE_NAME_1",
        },
        "mqtt_id": 123,
        "reboots": 0,
        "remote_name": "Remote Name 1 - 1",
    }
    assert resp.json() == expected_data


def test_put_device_tags_fails_on_invalid_device_id(populated_test_db):
    resp = client.put("/device/777/tags", json={"ids": [1, 2]})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Failed to add Tag id(s) of [1, 2] to Device of mqtt id 777 - No row was found when one was required"
    }


def test_put_device_tags_fails_on_invalid_tag_ids(populated_test_db):
    resp = client.put("/device/123/tags", json={"ids": [1234, 5678]})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Failed to add Tag id(s) of [1234, 5678] to Device of mqtt id 123 - No Tag object(s) with id(s) [1234, 5678] found."
    }


def test_put_device_tags_partial_success_202(populated_test_db):
    resp = client.put("/device/123/tags", json={"ids": [1, 5678]})
    assert resp.status_code == 202
    assert resp.json() == {
        "detail": "Some tag ids were added. Of the given tag ids, [1, 5678], the following were not added: [5678]",
        "device": {
            "id": 1,
            "mqtt_id": 123,
            "remote_name": "Remote Name 1 - 1",
            "name": "Test Device Name 1",
            "reboots": 0,
            "device_type": {
                "id": 1,
                "name": "TEST_DEVICE_TYPE_NAME_1",
            },
            "tags": [
                {
                    "id": 1,
                    "name": "Main Tag",
                },
            ],
        },
    }
