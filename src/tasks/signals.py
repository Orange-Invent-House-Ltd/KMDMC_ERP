from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks.models import Task
from user.tasks import recalculate_user_performance


@receiver(post_save, sender=Task)
def trigger_performance_recalculation(sender, instance, created, **kwargs):
    if not instance.pk:
        return

    try:
        old_status = Task.objects.get(pk=instance.pk).status
    except Task.DoesNotExist:
        old_status = None

    if old_status != 'completed' and instance.status == 'completed':
        recalculate_user_performance.delay(instance.assigned_to_id)
