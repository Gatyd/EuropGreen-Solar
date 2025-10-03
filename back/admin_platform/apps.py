from django.apps import AppConfig


class AdminPlatformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_platform'
    verbose_name = "Plateforme d'administration"
    
    def ready(self):
        """Appelé au démarrage de Django - Charge l'enregistrement auditlog"""
        # Import ici pour éviter les imports circulaires
        import admin_platform.auditlog_registry  # noqa
