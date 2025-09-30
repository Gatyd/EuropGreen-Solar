from rest_framework import serializers
from users.models import User
from .models import ProspectRequest
from offers.models import Offer


class AssignedToSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "role"]


class ProspectRequestSerializer(serializers.ModelSerializer):
    assigned_to = AssignedToSerializer(read_only=True)
    created_by = AssignedToSerializer(read_only=True)
    source = AssignedToSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="assigned_to", write_only=True, allow_null=True, required=False
    )
    source_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="source", write_only=True, allow_null=True, required=False
    )
    # Informations minimales de l'offre liée (si existante)
    offer = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProspectRequest
        fields = [
            "id", "last_name", "first_name", "email", "phone", "address", "housing_type",
            "electricity_bill", "status", "source_type", "source", "source_id", 
            "assigned_to", "assigned_to_id", # "notes",
            "converted_decision",
            "created_at", "updated_at", "created_by", "appointment_date", "offer"
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to", "created_by", "source"]

    def validate(self, attrs):
        return super().validate(attrs)

    def get_offer(self, obj: ProspectRequest):
        """Retourne l'info minimale de l'offre liée: { id, status } ou None."""
        try:
            offer: Offer = obj.offer  # OneToOne via related_name="offer"
            if not offer:
                return None
            return {"id": str(offer.id), "status": offer.status}
        except Offer.DoesNotExist:
            return None

    def update(self, instance: ProspectRequest, validated_data):
        # Si on change de statut et que l'ancien était 'closed' et le nouveau ne l'est plus -> reset converted_decision
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        if old_status == 'closed' and new_status != 'closed':
            # remettre à None si une décision existait
            instance.converted_decision = None
        return super().update(instance, validated_data)


class ClientProspectRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les clients qui consultent leurs prospects parrainés."""
    offer = serializers.SerializerMethodField(read_only=True)
    installation = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProspectRequest
        fields = [
            "id", "last_name", "first_name", "status", "created_at", 
            "offer", "installation"
        ]
        read_only_fields = fields

    def get_offer(self, obj: ProspectRequest):
        """Retourne l'info minimale de l'offre liée: { id, status } ou None."""
        try:
            offer: Offer = obj.offer
            if not offer:
                return None
            return {"id": str(offer.id), "status": offer.status}
        except Offer.DoesNotExist:
            return None

    def get_installation(self, obj: ProspectRequest):
        """Retourne les infos de commission de l'installation si l'offre existe et a été déplacée."""
        try:
            offer = obj.offer
            if not offer or not offer.installation_moved_at:
                return None
            # Récupérer l'installation via la relation inverse
            from installations.models import Form
            installation = Form.objects.filter(offer=offer).first()
            if not installation:
                return None
            return {
                "commission_amount": str(installation.commission_amount),
                "commission_paid": installation.commission_paid
            }
        except Exception:
            return None
