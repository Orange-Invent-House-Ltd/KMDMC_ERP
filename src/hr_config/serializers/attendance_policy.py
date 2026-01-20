from rest_framework import serializers
from hr_config.models import AttendancePolicy


class AttendancePolicySerializer(serializers.ModelSerializer):
    """Serializer for attendance policy (singleton)."""
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True, allow_null=True)
    shift_duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = AttendancePolicy
        fields = [
            'id',
            'shift_start_time',
            'shift_end_time',
            'shift_duration_hours',
            'late_grace_period_minutes',
            'enable_overtime',
            'overtime_threshold_minutes',
            'working_days_per_week',
            'working_days',
            'require_check_in',
            'require_check_out',
            'updated_by_name',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_shift_duration_hours(self, obj):
        """Calculate shift duration in hours."""
        from datetime import datetime

        start = datetime.combine(datetime.today(), obj.shift_start_time)
        end = datetime.combine(datetime.today(), obj.shift_end_time)

        duration = end - start
        return duration.total_seconds() / 3600

    def validate_working_days(self, value):
        """Validate working days array."""
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        if not isinstance(value, list):
            raise serializers.ValidationError("working_days must be an array")

        for day in value:
            if day.lower() not in valid_days:
                raise serializers.ValidationError(f"Invalid day: {day}")

        return [day.lower() for day in value]

    def validate(self, attrs):
        """Validate shift times."""
        start_time = attrs.get('shift_start_time', self.instance.shift_start_time if self.instance else None)
        end_time = attrs.get('shift_end_time', self.instance.shift_end_time if self.instance else None)

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'shift_end_time': 'Shift end time must be after start time'
            })

        return attrs

    def update(self, instance, validated_data):
        """Update singleton instance."""
        request = self.context.get('request')
        if request:
            validated_data['updated_by'] = request.user

        return super().update(instance, validated_data)
