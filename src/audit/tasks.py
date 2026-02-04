from celery import shared_task

from audit.contrib.logger import log_event
from correspondence.models import Correspondence


@shared_task
def log_audit_event_task(payload):
    correspondence_id = payload.pop("correspondence_id", None)

    if correspondence_id:
        payload["correspondence"] = Correspondence.objects.get(id=correspondence_id)
    return log_event(payload)
