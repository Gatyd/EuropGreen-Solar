"""
Configuration Celery pour EuropGreen Solar.

Permet l'exécution de tâches asynchrones et planifiées (rappels de tâches, etc.)

Les horaires et durées sont configurables via variables d'environnement dans settings.py :
- REMINDER_DAYS_BEFORE : Nombre de jours avant l'échéance (défaut: 3)
- REMINDER_HOURS_BEFORE : Nombre d'heures avant l'échéance (défaut: 3)
- REMINDER_TIME_HOUR : Heure des rappels quotidiens (défaut: 8)
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Définir le module de configuration Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EuropGreenSolar.settings')

app = Celery('EuropGreenSolar')

# Charger la configuration depuis les settings Django avec le namespace CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans tous les fichiers tasks.py des apps
app.autodiscover_tasks()

# Importer explicitement les tâches du projet (hors apps)
# Nécessaire car autodiscover_tasks() ne cherche que dans INSTALLED_APPS
app.autodiscover_tasks(['EuropGreenSolar'])

# Configuration des tâches périodiques
# Note: L'heure du rappel quotidien est prise depuis REMINDER_TIME_HOUR
app.conf.beat_schedule = {
    # Rappel X jours avant (tous les jours à l'heure configurée)
    'send-reminder-days-before': {
        'task': 'planning.tasks.send_reminder_days_before',
        'schedule': crontab(hour=getattr(settings, 'REMINDER_TIME_HOUR', 8), minute=0),
    },
    # Rappel X heures avant (toutes les 30 minutes pour vérifier)
    'send-reminder-hours-before': {
        'task': 'planning.tasks.send_reminder_hours_before',
        'schedule': crontab(minute='*/30'),  # Toutes les 30 minutes
    },
    # Notification à l'échéance (toutes les 15 minutes pour précision)
    'send-deadline-notification': {
        'task': 'planning.tasks.send_deadline_notification',
        'schedule': crontab(minute='*/15'),  # Toutes les 15 minutes
    },
}

# Fuseau horaire pour les tâches planifiées
app.conf.timezone = 'Europe/Paris'


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery."""
    print(f'Request: {self.request!r}')

