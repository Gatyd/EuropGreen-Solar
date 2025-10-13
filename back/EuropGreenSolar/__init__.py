"""
EuropGreen Solar - Configuration Django
"""

# Importer Celery app pour que Django le charge au démarrage
from .celery import app as celery_app

__all__ = ('celery_app',)
