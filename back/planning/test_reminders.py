"""
Script de test pour le système de rappels de tâches.

Usage:
    python manage.py shell < planning/test_reminders.py
    
Ou interactivement:
    python manage.py shell
    >>> exec(open('planning/test_reminders.py').read())
"""

from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
from planning.models import Task

User = get_user_model()

print("\n" + "="*60)
print("TEST DU SYSTÈME DE RAPPELS DE TÂCHES")
print("="*60 + "\n")

# 1. Vérifier qu'il y a des utilisateurs
print("1. Vérification des utilisateurs...")
users_count = User.objects.count()
print(f"   Nombre d'utilisateurs: {users_count}")

if users_count < 2:
    print("   ⚠️  Il faut au moins 2 utilisateurs pour tester le système")
    print("   Créez des utilisateurs via l'admin Django")
else:
    print("   ✅ OK\n")

# 2. Statistiques des tâches
print("2. Statistiques des tâches...")
total_tasks = Task.objects.count()
pending_tasks = Task.objects.filter(status='pending').count()
completed_tasks = Task.objects.filter(status='completed').count()

print(f"   Total des tâches: {total_tasks}")
print(f"   En attente: {pending_tasks}")
print(f"   Terminées: {completed_tasks}")
print("   ✅ OK\n")

# 3. Tâches éligibles pour rappel 3 jours
print("3. Tâches éligibles pour rappel 3 jours...")
now = timezone.now()
target_date_3d = (now + timedelta(days=3)).date()

tasks_3d = Task.objects.filter(
    due_date=target_date_3d,
    status__in=['pending', 'in_progress'],
    reminder_3days_sent=False
)
print(f"   Date cible: {target_date_3d}")
print(f"   Nombre de tâches: {tasks_3d.count()}")
if tasks_3d.exists():
    for task in tasks_3d[:3]:
        print(f"   - {task.title} (assignée à {task.assigned_to_name})")
print("   ✅ OK\n")

# 4. Tâches éligibles pour rappel 3h
print("4. Tâches éligibles pour rappel 3 heures...")
time_min = now + timedelta(hours=2, minutes=45)
time_max = now + timedelta(hours=3, minutes=15)

tasks_with_time = Task.objects.filter(
    due_date=time_min.date(),
    due_time__isnull=False,
    status__in=['pending', 'in_progress'],
    reminder_hours_sent=False
)

tasks_3h = []
for task in tasks_with_time:
    task_datetime = timezone.make_aware(
        timezone.datetime.combine(task.due_date, task.due_time)
    )
    if time_min <= task_datetime <= time_max:
        tasks_3h.append(task)

print(f"   Fenêtre: {time_min.strftime('%d/%m/%Y %H:%M')} - {time_max.strftime('%H:%M')}")
print(f"   Nombre de tâches: {len(tasks_3h)}")
if tasks_3h:
    for task in tasks_3h[:3]:
        print(f"   - {task.title} à {task.due_time.strftime('%H:%M')}")
print("   ✅ OK\n")

# 5. Tâches à l'échéance (pour notification au créateur)
print("5. Tâches à l'échéance...")
time_min_deadline = now - timedelta(minutes=15)
time_max_deadline = now + timedelta(minutes=15)

tasks_deadline = Task.objects.filter(
    due_date=now.date(),
    reminder_deadline_sent=False,
    assigned_by__isnull=False
)

print(f"   Fenêtre: {time_min_deadline.strftime('%d/%m/%Y %H:%M')} - {time_max_deadline.strftime('%H:%M')}")
print(f"   Nombre de tâches candidates: {tasks_deadline.count()}")
print("   ✅ OK\n")

# 6. Statistiques des rappels envoyés
print("6. Statistiques des rappels envoyés...")
sent_3d = Task.objects.filter(reminder_3days_sent=True).count()
sent_3h = Task.objects.filter(reminder_hours_sent=True).count()
sent_deadline = Task.objects.filter(reminder_deadline_sent=True).count()

print(f"   Rappels 3 jours envoyés: {sent_3d}")
print(f"   Rappels 3 heures envoyés: {sent_3h}")
print(f"   Notifications échéance envoyées: {sent_deadline}")
print("   ✅ OK\n")

# 7. Créer une tâche de test (si des utilisateurs existent)
if users_count >= 2:
    print("7. Création d'une tâche de test...")
    try:
        user1 = User.objects.first()
        user2 = User.objects.last()
        
        test_task = Task.objects.create(
            title="[TEST] Tâche de test du système de rappels",
            description="Cette tâche a été créée automatiquement pour tester le système de rappels.",
            assigned_to=user1,
            assigned_by=user2,
            due_date=(now + timedelta(days=3)).date(),
            due_time=now.time().replace(hour=14, minute=0, second=0),
            status='pending',
            priority='normal'
        )
        print(f"   ✅ Tâche créée avec succès (ID: {test_task.id})")
        print(f"   - Assignée à: {test_task.assigned_to_name}")
        print(f"   - Créée par: {test_task.assigned_by_name}")
        print(f"   - Échéance: {test_task.due_date} à {test_task.due_time.strftime('%H:%M')}")
        print(f"   - Cette tâche devrait déclencher un rappel 3j le {target_date_3d}")
        print("\n   Note: Vous pouvez supprimer cette tâche via l'admin Django")
    except Exception as e:
        print(f"   ⚠️  Erreur lors de la création: {e}")
else:
    print("7. Création d'une tâche de test...")
    print("   ⚠️  Impossible (pas assez d'utilisateurs)")

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60 + "\n")

# 8. Instructions suivantes
print("PROCHAINES ÉTAPES:")
print("-" * 60)
print("1. Vérifier que Redis tourne:")
print("   docker-compose ps redis")
print()
print("2. Vérifier que Celery Worker tourne:")
print("   docker-compose ps celery-worker")
print()
print("3. Vérifier que Celery Beat tourne:")
print("   docker-compose ps celery-beat")
print()
print("4. Consulter les logs Celery:")
print("   docker-compose logs -f celery-beat")
print()
print("5. Tester manuellement une tâche Celery:")
print("   python manage.py shell")
print("   >>> from planning.tasks import send_reminder_3_days_before")
print("   >>> result = send_reminder_3_days_before()")
print("   >>> print(result)")
print("-" * 60 + "\n")
