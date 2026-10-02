import datetime as dt


def sanitize_scheduler_kwargs(scheduler_kwargs: dict) -> dict:
    sanitized_scheduler_kwargs = {
        "trigger": scheduler_kwargs.get("trigger"),
    }
    if scheduler_kwargs['trigger'] == 'cron':
        for key in ('month', 'day', 'hour', 'minute', 'second'):
            if key in scheduler_kwargs:
                sanitized_scheduler_kwargs[key] = scheduler_kwargs[key]
    elif scheduler_kwargs['trigger'] == 'date':
        if 'run_date' in scheduler_kwargs:
            sanitized_scheduler_kwargs["run_date"] = scheduler_kwargs["run_date"]
        else:
            raise ValueError("run_date is required for date trigger")
    elif scheduler_kwargs['trigger'] == 'interval':
        sanitized_scheduler_kwargs["interval"] = scheduler_kwargs["interval"]
    return sanitized_scheduler_kwargs

def prepare_scheduler_kwargs(scheduler_kwargs: dict) -> dict:
    if scheduler_kwargs['trigger'] == 'date':
        return scheduler_kwargs | {
            "run_date": dt.datetime.strptime(scheduler_kwargs.get("run_date"), "%Y-%m-%d %H:%M:%S"),
        }
    return scheduler_kwargs
