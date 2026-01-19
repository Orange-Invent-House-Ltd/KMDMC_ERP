from rest_framework import serializers
from django.utils import timezone
from hr_config.models import PublicHoliday


class PublicHolidayListSerializer(serializers.ModelSerializer):
    """Serializer for listing public holidays."""
    date_display = serializers.SerializerMethodField()
    holiday_type_display = serializers.CharField(source='get_holiday_type_display', read_only=True)

    class Meta:
        model = PublicHoliday
        fields = [
            'id',
            'holiday_name',
            'date',
            'date_display',
            'year',
            'holiday_type',
            'holiday_type_display',
            'is_recurring',
            'created_at',
        ]

    def get_date_display(self, obj):
        """Formatted date for display."""
        return obj.date.strftime('%B %d, %Y')


class PublicHolidayDetailSerializer(serializers.ModelSerializer):
    """Full serializer for holiday details."""
    holiday_type_display = serializers.CharField(source='get_holiday_type_display', read_only=True)

    class Meta:
        model = PublicHoliday
        fields = '__all__'
        read_only_fields = ['year', 'created_at', 'updated_at']


class PublicHolidayCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating public holidays."""

    class Meta:
        model = PublicHoliday
        fields = [
            'holiday_name',
            'date',
            'holiday_type',
            'description',
            'is_recurring',
        ]

    def validate_date(self, value):
        """Ensure date is not in the past."""
        if value < timezone.now().date():
            raise serializers.ValidationError("Holiday date cannot be in the past.")
        return value


class PublicHolidayUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating public holidays."""

    class Meta:
        model = PublicHoliday
        fields = [
            'holiday_name',
            'date',
            'holiday_type',
            'description',
            'is_recurring',
        ]
