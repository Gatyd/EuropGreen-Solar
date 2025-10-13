"""
Commande Django pour tester manuellement le système de rappels.

Usage:
    # Tester tous les rappels
    python manage.py test_reminders

    # Tester uniquement le rappel X jours avant
    python manage.py test_reminders --days-before

    # Tester uniquement le rappel X heures avant
    python manage.py test_reminders --hours-before

    # Tester uniquement la notification d'échéance
    python manage.py test_reminders --deadline

    # Mode verbose pour voir les détails
    python manage.py test_reminders -v 2
"""

from django.core.management.base import BaseCommand
from planning.tasks import (
    send_reminder_days_before,
    send_reminder_hours_before,
    send_deadline_notification
)


class Command(BaseCommand):
    help = 'Teste manuellement le système de rappels de tâches'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            action='store_true',
            help='Tester uniquement le rappel X jours avant',
        )
        parser.add_argument(
            '--hours-before',
            action='store_true',
            help='Tester uniquement le rappel X heures avant',
        )
        parser.add_argument(
            '--deadline',
            action='store_true',
            help='Tester uniquement la notification d\'échéance',
        )

    def handle(self, *args, **options):
        # Si aucune option spécifique, tester tous les rappels
        test_all = not any([
            options['days_before'],
            options['hours_before'],
            options['deadline']
        ])

        if test_all or options['days_before']:
            self.stdout.write(self.style.WARNING('\n=== Test du rappel X jours avant ==='))
            try:
                send_reminder_days_before()
                self.stdout.write(self.style.SUCCESS('✓ Rappel X jours avant exécuté'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur: {e}'))

        if test_all or options['hours_before']:
            self.stdout.write(self.style.WARNING('\n=== Test du rappel X heures avant ==='))
            try:
                send_reminder_hours_before()
                self.stdout.write(self.style.SUCCESS('✓ Rappel X heures avant exécuté'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur: {e}'))

        if test_all or options['deadline']:
            self.stdout.write(self.style.WARNING('\n=== Test de la notification d\'échéance ==='))
            try:
                send_deadline_notification()
                self.stdout.write(self.style.SUCCESS('✓ Notification d\'échéance exécutée'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erreur: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Tests terminés'))
