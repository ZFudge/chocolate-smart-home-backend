import datetime as dt

from src.scheduler.utils import prepare_scheduler_kwargs, sanitize_scheduler_kwargs


def test_prepare_scheduler_kwargs():
    scheduler_kwargs = {
        "trigger": "date",
        "run_date": "2027-01-01 00:00:00",
    }
    assert prepare_scheduler_kwargs(scheduler_kwargs) == {
        "trigger": "date",
        "run_date": dt.datetime(2027, 1, 1, 0, 0, 0),
    }


def test_sanitize_scheduler_kwargs_cron():
    scheduler_kwargs = {
        "trigger": "cron",
        "minute": "*/3",
        "hour": "*/2",
        "day": "*/4",
        "month": "*/5",
        "second": "*/6",
        "not_allowed": "test",
    }
    assert sanitize_scheduler_kwargs(scheduler_kwargs) == {
        "trigger": "cron",
        "minute": "*/3",
        "hour": "*/2",
        "day": "*/4",
        "month": "*/5",
        "second": "*/6",
    }
