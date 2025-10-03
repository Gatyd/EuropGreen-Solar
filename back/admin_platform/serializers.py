"""
Serializers pour la plateforme d'administration.
"""

from rest_framework import serializers
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
