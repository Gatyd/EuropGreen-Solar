from rest_framework import serializers
from users.models import User
from .models import ProspectRequest


class AssignedToSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "role"]


class ProspectRequestSerializer(serializers.ModelSerializer):
    assigned_to = AssignedToSerializer(read_only=True)
    created_by = AssignedToSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="assigned_to", write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = ProspectRequest
        fields = [
            "id", "last_name", "first_name", "email", "phone", "address", "housing_type",
            "electricity_bill", "status", "source", "assigned_to", "assigned_to_id", # "notes",
            "created_at", "updated_at", "created_by", "appointment_date"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to", "created_by"]

    def validate(self, attrs):
        return super().validate(attrs)
