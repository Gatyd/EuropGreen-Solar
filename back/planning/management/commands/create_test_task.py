"""
Commande Django pour créer rapidement une tâche de test pour les rappels.

Usage:
    # Créer une tâche pour tester le rappel X jours avant
    python manage.py create_test_task --days-before

    # Créer une tâche pour tester le rappel X heures avant
    python manage.py create_test_task --hours-before

    # Créer une tâche pour tester la notification d'échéance
    python manage.py create_test_task --deadline

    # Spécifier un email de test différent
    python manage.py create_test_task --days-before --email test@example.com
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from planning.models import Task
from users.models import User


class Command(BaseCommand):
    help = 'Crée une tâche de test pour le système de rappels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            action='store_true',
            help='Créer une tâche pour tester le rappel X jours avant',
        )
        parser.add_argument(
            '--hours-before',
            action='store_true',
            help='Créer une tâche pour tester le rappel X heures avant',
        )
        parser.add_argument(
            '--deadline',
            action='store_true',
            help='Créer une tâche pour tester la notification d\'échéance',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email du destinataire (défaut: premier utilisateur trouvé)',
        )

    def handle(self, *args, **options):
        # Vérifier qu'au moins une option est spécifiée
        if not any([options['days_before'], options['hours_before'], options['deadline']]):
            raise CommandError(
                'Vous devez spécifier au moins une option: '
                '--days-before, --hours-before ou --deadline'
            )

        # Trouver un utilisateur pour assigner la tâche
        if options['email']:
            try:
                user = User.objects.get(email=options['email'])
            except User.DoesNotExist:
                raise CommandError(f'Aucun utilisateur trouvé avec l\'email: {options["email"]}')
        else:
            user = User.objects.filter(is_active=True).first()
            if not user:
                raise CommandError('Aucun utilisateur actif trouvé dans la base de données')

        self.stdout.write(f'Utilisateur cible: {user.email}')

        now = timezone.now()
        days_before = getattr(settings, 'REMINDER_DAYS_BEFORE', 3)
        hours_before = getattr(settings, 'REMINDER_HOURS_BEFORE', 3)

        created_tasks = []

        # Créer une tâche pour le rappel X jours avant
        if options['days_before']:
            due_date = (now + timedelta(days=days_before)).date()
            task = Task.objects.create(
                title=f'[TEST] Rappel {days_before} jours avant',
                description=f'Tâche de test créée le {now.strftime("%d/%m/%Y à %H:%M")}. '
                           f'Vous devriez recevoir un rappel car l\'échéance est dans {days_before} jour(s).',
                due_date=due_date,
                due_time=timezone.now().time(),
                priority=Task.TaskPriority.MEDIUM,
                status=Task.TaskStatus.PENDING,
                assigned_to=user,
                assigned_by=user,
            )
            created_tasks.append(task)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Tâche créée (ID: {task.id}) - Échéance: {due_date} '
                    f'(dans {days_before} jours)'
                )
            )

        # Créer une tâche pour le rappel X heures avant
        if options['hours_before']:
            target_datetime = now + timedelta(hours=hours_before)
            task = Task.objects.create(
                title=f'[TEST] Rappel {hours_before} heures avant',
                description=f'Tâche de test créée le {now.strftime("%d/%m/%Y à %H:%M")}. '
                           f'Vous devriez recevoir un rappel car l\'échéance est dans {hours_before} heure(s).',
                due_date=target_datetime.date(),
                due_time=target_datetime.time(),
                priority=Task.TaskPriority.HIGH,
                status=Task.TaskStatus.PENDING,
                assigned_to=user,
                assigned_by=user,
            )
            created_tasks.append(task)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Tâche créée (ID: {task.id}) - Échéance: '
                    f'{target_datetime.strftime("%d/%m/%Y à %H:%M")} '
                    f'(dans {hours_before} heures)'
                )
            )

        # Créer une tâche pour la notification d'échéance
        if options['deadline']:
            # Échéance = maintenant (ou il y a 5 minutes pour être sûr)
            target_datetime = now - timedelta(minutes=5)
            task = Task.objects.create(
                title='[TEST] Notification d\'échéance',
                description=f'Tâche de test créée le {now.strftime("%d/%m/%Y à %H:%M")}. '
                           f'L\'échéance est déjà atteinte, vous devriez recevoir une notification.',
                due_date=target_datetime.date(),
                due_time=target_datetime.time(),
                priority=Task.TaskPriority.URGENT,
                status=Task.TaskStatus.PENDING,
                assigned_to=user,
                assigned_by=user,
            )
            created_tasks.append(task)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Tâche créée (ID: {task.id}) - Échéance: '
                    f'{target_datetime.strftime("%d/%m/%Y à %H:%M")} '
                    f'(échéance dépassée)'
                )
            )

        # Instructions de test
        self.stdout.write(self.style.WARNING('\n📧 Pour tester l\'envoi des rappels, exécutez:'))
        self.stdout.write('   python manage.py test_reminders')
        self.stdout.write('\nOu dans Docker:')
        self.stdout.write('   docker-compose exec web python manage.py test_reminders')

        # Afficher les IDs des tâches créées
        if created_tasks:
            task_ids = ', '.join(str(t.id) for t in created_tasks)
            self.stdout.write(self.style.WARNING(f'\n🗑️  Pour supprimer ces tâches de test après:'))
            self.stdout.write(f'   python manage.py shell -c "from planning.models import Task; Task.objects.filter(id__in=[{task_ids}]).delete()"')
