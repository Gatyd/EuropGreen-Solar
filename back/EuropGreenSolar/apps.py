"""
Configuration de l'application EuropGreenSolar
Charge l'enregistrement auditlog au démarrage
"""
from django.apps import AppConfig


class EuropGreenSolarConfig(AppConfig):
    name = 'EuropGreenSolar'
    verbose_name = "EuropGreen Solar"
    
    def ready(self):
        """Appelé au démarrage de Django"""
        # Import ici pour éviter les imports circulaires
        import EuropGreenSolar.auditlog_registry  # noqa
