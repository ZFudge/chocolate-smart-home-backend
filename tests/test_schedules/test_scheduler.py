import pytest
from unittest.mock import call, patch

from src.scheduler import schemas, crud


def test_create_job_creates_and_returns_new_job(populated_test_db):
    schema = schemas.JobToSchedule(
        job_id="test",
        device_type_name="TEST_DEVICE_TYPE_NAME_1",
        mqtt_ids=[123],
        message_kvp=schemas.KVP(
            key="test",
            value=True,
        ),
        scheduler_kwargs=dict(
            minute="*/3",
            trigger="cron",
        ),
    )
    job = crud.create_job(schema)
    assert job is not None
    assert job.job_id == "test"
    assert job.device_type_id == 1
    assert len(job.devices) == 1
    assert job.devices[0].mqtt_id == 123
    assert job.message_kvp == {
        "key": "test",
        "value": True,
    }
    assert job.active is True


def test_create_job_invalid_device_type_name_raises_error(populated_test_db):
    schema = schemas.JobToSchedule(
        job_id="test",
        name="Test Job",
        device_type_name="INVALID_DEVICE_TYPE_NAME",
        mqtt_ids=[123],
        message_kvp=schemas.KVP(
            key="test",
            value=True,
        ),
        scheduler_kwargs=dict(
            minute="*/3",
            trigger="cron",
        ),
        active=True,
    )
    with pytest.raises(ValueError):
        crud.create_job(schema)


def test_create_job_invalid_mqtt_ids_raises_error(populated_test_db):
    schema = schemas.JobToSchedule(
        job_id="test",
        device_type_name="TEST_DEVICE_TYPE_NAME_1",
        mqtt_ids=[123, 456],
        message_kvp=schemas.KVP(
            key="test",
            value=True,
        ),
        scheduler_kwargs=dict(
            key="test",
            value=True,
        ),
        active=True,
    )
    with pytest.raises(ValueError):
        crud.create_job(schema)


def test_get_jobs_returns_job(populated_test_db):
    jobs = crud.get_jobs()
    assert jobs is not None
    assert len(jobs) == 1
    assert jobs[0].job_id == "test_job_id"
    assert jobs[0].name == "Test Job 1"
    assert jobs[0].active is True
    assert jobs[0].scheduler_kwargs == {
        "minute": "*/3",
        "trigger": "cron",
    }
    assert jobs[0].message_kvp == {
        "key": "test_key",
        "value": True,
    }


def test_load_jobs_from_db_schedules_jobs_from_db(
    populated_test_db, job_loaded_scheduler
):
    job = job_loaded_scheduler.get_job("test_job_id")
    assert job is not None
    assert job.id == "test_job_id"


def test_get_job_by_id_returns_job(populated_test_db):
    job = crud.get_job_by_id("test_job_id")
    assert job is not None
    assert job.job_id == "test_job_id"
    assert job.name == "Test Job 1"


def test_delete_job_by_id_deletes_job(populated_test_db, job_loaded_scheduler):
    crud.delete_job_by_id("test_job_id")
    assert crud.get_job_by_id("test_job_id") is None
    assert len(crud.get_jobs()) == 0


def test_delete_job_by_id_invalid_id_does_not_raise_error(populated_test_db):
    with patch("src.scheduler.crud.logger.warning") as mock_logger:
        crud.delete_job_by_id("INVALID_JOB_ID")
        mock_logger.assert_has_calls(
            [
                call(
                    "Job INVALID_JOB_ID not found in scheduler: 'No job by the id of INVALID_JOB_ID was found'"
                ),
                call("Job INVALID_JOB_ID not found in database"),
            ]
        )


def test_modify_job_by_id_modifies_job(populated_test_db, job_loaded_scheduler):
    modified_job = schemas.ModifyJob(
        message_kvp=schemas.KVP(
            key="test_key_2",
            value=5,
        ),
        active=False,
    )
    job = crud.modify_job_by_id("test_job_id", modified_job)
    assert job is not None
    assert job.message_kvp == {
        "key": "test_key_2",
        "value": 5,
    }
    assert job.active is False
