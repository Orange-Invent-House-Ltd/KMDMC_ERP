from rest_framework import serializers
from hr_config.models import LeaveType


class LeaveTypeListSerializer(serializers.ModelSerializer):
    """Serializer for listing leave types."""
    accrual_display = serializers.SerializerMethodField()
    accrual_frequency_display = serializers.CharField(source='get_accrual_frequency_display', read_only=True)

    class Meta:
        model = LeaveType
        fields = [
            'id',
            'leave_type_name',
            'allowance_days',
            'accrual_frequency',
            'accrual_frequency_display',
            'accrual_rate',
            'accrual_display',
            'is_paid',
            'is_active',
            'color_code',
            'created_at',
            'updated_at',
        ]

    def get_accrual_display(self, obj):
        """Human-readable accrual info."""
        if obj.accrual_frequency == 'monthly' and obj.accrual_rate:
            return f"{obj.accrual_rate} days/month"
        elif obj.accrual_frequency == 'yearly':
            return f"{obj.allowance_days} days/year"
        else:
            return f"{obj.allowance_days} days per event"


class LeaveTypeDetailSerializer(serializers.ModelSerializer):
    """Full serializer for leave type details."""
    accrual_frequency_display = serializers.CharField(source='get_accrual_frequency_display', read_only=True)

    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveTypeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating leave types."""

    class Meta:
        model = LeaveType
        fields = [
            'leave_type_name',
            'description',
            'allowance_days',
            'accrual_frequency',
            'accrual_rate',
            'requires_documentation',
            'is_paid',
            'is_active',
            'color_code',
        ]

    def validate(self, attrs):
        """Validate and auto-calculate accrual rate based on frequency."""
        accrual_frequency = attrs.get('accrual_frequency')
        allowance_days = attrs.get('allowance_days')

        # Auto-calculate accrual_rate if not provided
        if accrual_frequency == 'monthly' and not attrs.get('accrual_rate'):
            attrs['accrual_rate'] = allowance_days / 12
        elif accrual_frequency == 'yearly' and not attrs.get('accrual_rate'):
            attrs['accrual_rate'] = allowance_days

        return attrs


class LeaveTypeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating leave types."""

    class Meta:
        model = LeaveType
        fields = [
            'leave_type_name',
            'description',
            'allowance_days',
            'accrual_frequency',
            'accrual_rate',
            'requires_documentation',
            'is_paid',
            'is_active',
            'color_code',
        ]

    def validate(self, attrs):
        """Validate and auto-calculate accrual rate based on frequency."""
        accrual_frequency = attrs.get('accrual_frequency', self.instance.accrual_frequency if self.instance else None)
        allowance_days = attrs.get('allowance_days', self.instance.allowance_days if self.instance else None)

        # Auto-calculate accrual_rate if not provided
        if accrual_frequency == 'monthly' and 'accrual_rate' not in attrs:
            attrs['accrual_rate'] = allowance_days / 12
        elif accrual_frequency == 'yearly' and 'accrual_rate' not in attrs:
            attrs['accrual_rate'] = allowance_days

        return attrs
