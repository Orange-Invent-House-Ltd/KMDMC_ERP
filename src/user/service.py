from django.db.models import Avg, F, ExpressionWrapper, DurationField
from tasks.models import Task
from user.models.models import PerformanceRecord


def update_user_avg_task_time(user):
    completed_tasks = Task.objects.filter(
        assigned_to=user,
        status='completed',
        started_at__isnull=False,
        completed_at__isnull=False
    ).annotate(
        duration=ExpressionWrapper(
            F('completed_at') - F('started_at'),
            output_field=DurationField()
        )
    )

    avg_duration = completed_tasks.aggregate(avg=Avg('duration'))['avg']

    avg_hours = (
        round(avg_duration.total_seconds() / 3600, 2)
        if avg_duration else 0
    )

    performance, _ = PerformanceRecord.objects.get_or_create(user=user)

    performance.avg_response_time_hours = avg_hours
    performance.tasks_completed = completed_tasks.count()
    performance.save()
