from fastapi.testclient import TestClient

from src.scheduler import crud
from src.scheduler.sched_app import sched_app

sched_client = TestClient(sched_app)


def test_route_get_jobs_returns_jobs(populated_test_db):
    resp = sched_client.get("/scheduler")
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "job_id": "test_job_id",
            "name": "Test Job 1",
            "device_type_id": 1,
            "mqtt_ids": [345],
            "message_kvp": {
                "key": "test_key",
                "value": True,
            },
            "scheduler_kwargs": {
                "minute": "*/3",
                "trigger": "cron",
            },
            "active": True,
        }
    ]


def test_route_get_job_returns_job(populated_test_db):
    resp = sched_client.get("/scheduler/test_job_id")
    assert resp.status_code == 200
    assert resp.json() == {
        "job_id": "test_job_id",
        "name": "Test Job 1",
        "device_type_id": 1,
        "mqtt_ids": [345],
        "message_kvp": {
            "key": "test_key",
            "value": True,
        },
        "scheduler_kwargs": {
            "minute": "*/3",
            "trigger": "cron",
        },
        "active": True,
    }


def test_route_get_job_invalid_id_returns_404(populated_test_db):
    resp = sched_client.get("/scheduler/INVALID_JOB_ID")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Job with id INVALID_JOB_ID not found."}


def test_route_post_job_creates_cron_job(populated_test_db, job_loaded_scheduler):
    post_data = {
        "name": "Test Cron Job",
        "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
        "mqtt_ids": [234],
        "message_kvp": {
            "key": "test_key_2",
            "value": "test_value_2",
        },
        "scheduler_kwargs": {
            "minute": "*/3",
            "trigger": "cron",
        },
        "active": True,
    }
    resp = sched_client.post("/scheduler", json=post_data)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["name"] == "Test Cron Job"
    assert resp_data["device_type_id"] == 2
    assert resp_data["mqtt_ids"] == [234]
    assert resp_data["message_kvp"] == {
        "key": "test_key_2",
        "value": "test_value_2",
    }
    assert resp_data["scheduler_kwargs"] == {
        "minute": "*/3",
        "trigger": "cron",
    }
    assert resp_data["active"] is True


def test_route_post_job_creates_date_job(populated_test_db, job_loaded_scheduler):
    post_data = {
        "name": "Test Date Job",
        "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
        "mqtt_ids": [234],
        "message_kvp": {
            "key": "test_key_2",
            "value": "test_value_2",
        },
        "scheduler_kwargs": {
            "run_date": "2027-01-01 00:00:00",
            "trigger": "date",
        },
        "active": True,
    }
    resp = sched_client.post("/scheduler", json=post_data)
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["name"] == "Test Date Job"
    assert resp_data["device_type_id"] == 2
    assert resp_data["mqtt_ids"] == [234]
    assert resp_data["message_kvp"] == {
        "key": "test_key_2",
        "value": "test_value_2",
    }
    assert resp_data["scheduler_kwargs"] == {
        "run_date": "2027-01-01 00:00:00",
        "trigger": "date",
    }
    assert resp_data["active"] is True


def test_route_delete_job_deletes_job(populated_test_db, job_loaded_scheduler):
    resp = sched_client.delete("/scheduler/test_job_id")
    assert resp.status_code == 204
    assert crud.get_job_by_id("test_job_id") is None
    assert len(crud.get_jobs()) == 0


def test_route_put_job_modifies_job(populated_test_db, job_loaded_scheduler):
    put_data = {
        "job_id": "test_job_id",
        "name": "New Test Job Name",
        "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
        "mqtt_ids": [234, 345],
        "message_kvp": {
            "key": "test_key_2",
            "value": "test_value_2",
        },
        "scheduler_kwargs": {
            "minute": "*",
            "trigger": "cron",
        },
        "active": False,
    }
    resp = sched_client.put("/scheduler/", json=put_data)
    assert resp.status_code == 200
    assert resp.json() == {
        "job_id": "test_job_id",
        "name": "New Test Job Name",
        "device_type_id": 1,
        "mqtt_ids": [345, 234],
        "message_kvp": {
            "key": "test_key_2",
            "value": "test_value_2",
        },
        "scheduler_kwargs": {
            "minute": "*",
            "trigger": "cron",
        },
        "active": False,
    }


def test_route_put_job_fails_with_nonexistent_job_id(
    populated_test_db, job_loaded_scheduler
):
    put_data = {
        "job_id": "nonexistent_job_id",
        "name": "New Test Job Name",
        "device_type_name": "TEST_DEVICE_TYPE_NAME_2",
        "mqtt_ids": [234, 345],
        "message_kvp": {
            "key": "test_key_2",
            "value": "test_value_2",
        },
        "scheduler_kwargs": {
            "minute": "*/3",
            "trigger": "cron",
        },
        "active": False,
    }
    resp = sched_client.put("/scheduler/", json=put_data)
    assert resp.status_code == 404
