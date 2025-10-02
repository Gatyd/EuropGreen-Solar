"""
Modèles pour la plateforme d'administration.
"""

from django.db import models
from django.utils import timezone


class EmailLog(models.Model):
    """
    Enregistre les informations des emails envoyés par l'application.
    Permet un suivi et un audit des communications.
    """
    
    # Informations sur les destinataires
    recipients = models.JSONField(
        help_text="Liste des adresses email destinataires"
    )
    
    # Contenu de l'email
    subject = models.CharField(
        max_length=500,
        help_text="Sujet de l'email"
    )
    html_content = models.TextField(
        help_text="Contenu HTML complet de l'email"
    )
    plain_content = models.TextField(
        blank=True,
        help_text="Version texte de l'email"
    )
    
    # Métadonnées d'envoi
    from_email = models.CharField(
        max_length=255,
        help_text="Adresse d'expéditeur"
    )
    template_used = models.CharField(
        max_length=255,
        blank=True,
        help_text="Template utilisé pour générer l'email"
    )
    send_method = models.CharField(
        max_length=50,
        choices=[
            ('mailgun', 'Mailgun'),
            ('smtp', 'SMTP'),
        ],
        help_text="Méthode d'envoi utilisée"
    )
    
    # Horodatage
    sent_at = models.DateTimeField(
        default=timezone.now,
        help_text="Date et heure d'envoi"
    )
    
    # Pièces jointes
    attachments_info = models.JSONField(
        blank=True,
        null=True,
        help_text="Informations sur les pièces jointes (noms de fichiers, types MIME)"
    )
    
    # Contexte optionnel (sans données sensibles)
    context_snapshot = models.JSONField(
        blank=True,
        null=True,
        help_text="Snapshot du contexte utilisé (excluant les données sensibles)"
    )
    
    class Meta:
        db_table = 'admin_platform_email_log'
        ordering = ['-sent_at']
        verbose_name = "Log d'email"
        verbose_name_plural = "Logs d'emails"
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['send_method']),
        ]
    
    def __str__(self):
        recipients_str = ', '.join(self.recipients) if isinstance(self.recipients, list) else str(self.recipients)
        return f"{self.subject} → {recipients_str} ({self.sent_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_recipients_display(self):
        """Retourne une représentation lisible des destinataires."""
        if isinstance(self.recipients, list):
            return ', '.join(self.recipients)
        return str(self.recipients)
    
    def has_attachments(self):
        """Indique si l'email contient des pièces jointes."""
        return bool(self.attachments_info)

