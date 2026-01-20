from audit.models import AuditLog, LogParams


def log_event(event: dict):
    log_params = LogParams(**event)
    AuditLog.log_action(log_params)
    return {"status": "Logged", "payload": event}
