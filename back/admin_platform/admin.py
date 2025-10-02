"""
Configuration de l'interface d'administration pour admin_platform.
"""

from django.contrib import admin
from .models import EmailLog


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Interface d'administration basique pour consulter les logs d'emails."""
    
    list_display = ['id', 'subject', 'recipients', 'send_method', 'sent_at']
    list_filter = ['send_method', 'sent_at']
    search_fields = ['subject', 'recipients', 'from_email']
    readonly_fields = ['recipients', 'subject', 'html_content', 'plain_content', 
                      'from_email', 'template_used', 'send_method', 'sent_at', 'attachments_info']
    date_hierarchy = 'sent_at'
    ordering = ['-sent_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


