"""
Serializers pour la plateforme d'administration.
"""

from rest_framework import serializers
from auditlog.models import LogEntry
from .models import EmailLog


class EmailLogSerializer(serializers.ModelSerializer):
    """
    Serializer pour les logs d'emails.
    """
    
    recipients_display = serializers.SerializerMethodField()
    has_attachments = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailLog
        fields = [
            'id',
            'recipients',
            'recipients_display',
            'subject',
            'html_content',
            'plain_content',
            'from_email',
            'template_used',
            'send_method',
            'sent_at',
            'attachments_info',
            'has_attachments',
        ]
        read_only_fields = fields
    
    def get_recipients_display(self, obj):
        """Retourne une chaîne formatée des destinataires."""
        return obj.get_recipients_display()
    
    def get_has_attachments(self, obj):
        """Indique si l'email a des pièces jointes."""
        return obj.has_attachments()


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer pour les logs d'audit (django-auditlog).
    """
    
    actor_name = serializers.SerializerMethodField()
    actor_email = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    object_type = serializers.CharField(source='content_type.model', read_only=True)
    object_app = serializers.CharField(source='content_type.app_label', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id',
            'timestamp',
            'action',
            'action_display',
            'object_type',
            'object_app',
            'object_repr',
            'object_pk',
            'changes',
            'actor_name',
            'actor_email',
            'remote_addr',
            'additional_data',
        ]
        read_only_fields = fields
    
    def get_actor_name(self, obj):
        """Retourne le nom complet de l'acteur."""
        if obj.actor:
            return f"{obj.actor.first_name} {obj.actor.last_name}" or obj.actor.email
        return 'Système'
    
    def get_actor_email(self, obj):
        """Retourne l'email de l'acteur."""
        return obj.actor.email if obj.actor else None
