from celery import shared_task

from audit.contrib.logger import log_event


@shared_task
def log_audit_event_task(payload):
    return log_event(payload)
