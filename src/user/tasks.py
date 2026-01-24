from celery import shared_task
from core.resources.email_service_v2 import EmailClientV2

from django.contrib.auth import get_user_model

@shared_task
def send_invitation_email(email, values):
    EmailClientV2.send_account_verification_email(email, values)


@shared_task
def send_onboarding_successful_email(email, values):
    EmailClientV2.send_onboarding_successful_email(email, values)


@shared_task
def send_system_onboarding_successful_email(email, values):
    EmailClientV2.send_system_onboarding_successful_email(email, values)


@shared_task
def login_notification_email(email, values):
    EmailClientV2.send_login_notification_email(email, values)


@shared_task
def send_one_time_login_code_email(email, values):
    EmailClientV2.send_one_time_login_code_email(email, values)


@shared_task
def send_security_question_otp_email(email, values):
    EmailClientV2.send_security_question_otp_email(email, values)


@shared_task
def send_one_time_verification_code_email(email, values):
    EmailClientV2.send_one_time_verification_code_email(email, values)


@shared_task
def send_reset_password_request_email(email, values):
    EmailClientV2.send_reset_password_request_email(email, values)


@shared_task
def send_reset_password_otp_request_email(email, values):
    EmailClientV2.send_reset_password_otp_request_email(email, values)


@shared_task
def send_reset_password_success_email(email, values):
    EmailClientV2.send_reset_password_success_email(email, values)


@shared_task
def reset_password_notification_email(email, values):
    EmailClientV2.reset_password_notification_email(email, values)


@shared_task
def send_security_question_update_notification_email(email, values):
    EmailClientV2.send_security_question_update_notification_email(email, values)


@shared_task
def send_security_question_notification_email(email, values):
    EmailClientV2.send_security_question_notification_email(email, values)


@shared_task
def send_transfer_PIN_notification_email(email, values):
    EmailClientV2.send_transfer_PIN_notification_email(email, values)



from user.service import update_user_avg_task_time

User = get_user_model()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={'max_retries': 3})
def recalculate_user_performance(self, user_id):
    user = User.objects.get(id=user_id)
    update_user_avg_task_time(user)
