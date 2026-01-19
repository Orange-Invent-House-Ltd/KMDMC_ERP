from rest_framework import serializers
from hr_config.models import AppraisalTemplate


class AppraisalTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    section_count = serializers.SerializerMethodField()

    class Meta:
        model = AppraisalTemplate
        fields = [
            'id',
            'template_id',
            'template_name',
            'description',
            'status',
            'status_display',
            'section_count',
            'created_by_name',
            'created_at',
            'updated_at',
        ]

    def get_section_count(self, obj):
        """Count sections in template_content."""
        return len(obj.template_content.get('sections', []))


class AppraisalTemplateDetailSerializer(serializers.ModelSerializer):
    """Full serializer with template content for detail view."""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AppraisalTemplate
        fields = [
            'id',
            'template_id',
            'template_name',
            'description',
            'status',
            'status_display',
            'template_content',
            'created_by_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['template_id', 'created_at', 'updated_at']


class AppraisalTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appraisal templates."""

    class Meta:
        model = AppraisalTemplate
        fields = [
            'template_name',
            'description',
            'status',
            'template_content',
        ]

    def validate_template_content(self, value):
        """Validate JSON structure."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("template_content must be a JSON object")

        if 'sections' not in value:
            raise serializers.ValidationError("template_content must contain 'sections' key")

        if not isinstance(value['sections'], list):
            raise serializers.ValidationError("'sections' must be an array")

        # Validate each section
        for idx, section in enumerate(value['sections']):
            # Section must have name
            if 'section_name' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} missing 'section_name'"
                )

            # Section must have weight
            if 'weight' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} ('{section.get('section_name')}') missing 'weight'"
                )

            # Validate weight is a number
            try:
                weight = float(section['weight'])
                if weight < 0 or weight > 100:
                    raise serializers.ValidationError(
                        f"Section {idx} weight must be between 0 and 100"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Section {idx} weight must be a number"
                )

            # Section must have criteria array (can be empty for non-scored sections)
            if 'criteria' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} ('{section.get('section_name')}') missing 'criteria' array"
                )

            if not isinstance(section['criteria'], list):
                raise serializers.ValidationError(
                    f"Section {idx} 'criteria' must be an array"
                )

            # Validate each criterion
            for c_idx, criterion in enumerate(section['criteria']):
                if 'criterion_name' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} missing 'criterion_name'"
                    )
                if 'scoring_method' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} ('{criterion.get('criterion_name')}') missing 'scoring_method'"
                    )
                if 'weight' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} ('{criterion.get('criterion_name')}') missing 'weight'"
                    )

        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class AppraisalTemplateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating appraisal templates."""

    class Meta:
        model = AppraisalTemplate
        fields = [
            'template_name',
            'description',
            'status',
            'template_content',
        ]

    def validate_template_content(self, value):
        """Validate JSON structure (same as create)."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("template_content must be a JSON object")

        if 'sections' not in value:
            raise serializers.ValidationError("template_content must contain 'sections' key")

        if not isinstance(value['sections'], list):
            raise serializers.ValidationError("'sections' must be an array")

        # Validate each section
        for idx, section in enumerate(value['sections']):
            # Section must have name
            if 'section_name' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} missing 'section_name'"
                )

            # Section must have weight
            if 'weight' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} ('{section.get('section_name')}') missing 'weight'"
                )

            # Validate weight is a number
            try:
                weight = float(section['weight'])
                if weight < 0 or weight > 100:
                    raise serializers.ValidationError(
                        f"Section {idx} weight must be between 0 and 100"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Section {idx} weight must be a number"
                )

            # Section must have criteria array (can be empty for non-scored sections)
            if 'criteria' not in section:
                raise serializers.ValidationError(
                    f"Section {idx} ('{section.get('section_name')}') missing 'criteria' array"
                )

            if not isinstance(section['criteria'], list):
                raise serializers.ValidationError(
                    f"Section {idx} 'criteria' must be an array"
                )

            # Validate each criterion
            for c_idx, criterion in enumerate(section['criteria']):
                if 'criterion_name' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} missing 'criterion_name'"
                    )
                if 'scoring_method' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} ('{criterion.get('criterion_name')}') missing 'scoring_method'"
                    )
                if 'weight' not in criterion:
                    raise serializers.ValidationError(
                        f"Section {idx}, criterion {c_idx} ('{criterion.get('criterion_name')}') missing 'weight'"
                    )

        return value
