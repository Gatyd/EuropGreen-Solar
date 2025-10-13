"""
Tâches Celery pour le système de rappels de tâches.

Ces tâches sont exécutées périodiquement par Celery Beat selon le planning défini
dans EuropGreenSolar/celery.py.

Les durées sont configurables via variables d'environnement pour plus de flexibilité.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from django.conf import settings
from datetime import timedelta

from planning.models import Task
from EuropGreenSolar.email_utils import send_mail


@shared_task(name='planning.tasks.send_reminder_days_before')
def send_reminder_days_before():
    """
    Envoie un rappel X jours avant l'échéance de la tâche.
    Le nombre de jours est configurable via REMINDER_DAYS_BEFORE.
    Exécuté tous les jours à l'heure configurée (REMINDER_TIME_HOUR).
    """
    now = timezone.now()
    days_before = getattr(settings, 'REMINDER_DAYS_BEFORE', 3)
    target_date = (now + timedelta(days=days_before)).date()
    
    # Rechercher les tâches non terminées dont l'échéance est dans X jours
    # et pour lesquelles le rappel n'a pas encore été envoyé
    tasks = Task.objects.filter(
        due_date=target_date,
        status__in=[Task.TaskStatus.PENDING, Task.TaskStatus.IN_PROGRESS],
        reminder_3days_sent=False
    ).select_related('assigned_to', 'assigned_by', 'related_installation')
    
    sent_count = 0
    failed_count = 0
    
    for task in tasks:
        try:
            # Vérifier que l'utilisateur assigné a un email
            if not task.assigned_to.email:
                print(f"[Rappel {days_before}j] Tâche {task.id}: utilisateur sans email")
                continue
            
            # Préparer le contexte pour le template
            context = {
                'task': task,
                'days_remaining': days_before,
                'frontend_url': '',  # Sera rempli par email_utils
            }
            
            # Envoyer l'email (sans emoji dans le sujet)
            success, message = send_mail(
                template='emails/planning/task_reminder_3_days.html',
                context=context,
                subject=f"Rappel : {task.title} - Échéance dans {days_before} jours",
                to=task.assigned_to.email,
                save_to_log=True,
            )
            
            if success:
                # Marquer le rappel comme envoyé
                task.reminder_3days_sent = True
                task.save(update_fields=['reminder_3days_sent'])
                sent_count += 1
                print(f"[Rappel {days_before}j] Envoyé pour tâche {task.id} à {task.assigned_to.email}")
            else:
                failed_count += 1
                print(f"[Rappel {days_before}j] Échec pour tâche {task.id}: {message}")
                
        except Exception as e:
            failed_count += 1
            print(f"[Rappel {days_before}j] Erreur pour tâche {task.id}: {e}")
    
    print(f"[Rappel {days_before}j] Résumé: {sent_count} envoyés, {failed_count} échecs")
    return {'sent': sent_count, 'failed': failed_count}


@shared_task(name='planning.tasks.send_reminder_hours_before')
def send_reminder_hours_before():
    """
    Envoie un rappel X heures avant l'heure d'échéance de la tâche.
    Le nombre d'heures est configurable via REMINDER_HOURS_BEFORE.
    Exécuté toutes les 30 minutes pour vérifier les tâches à venir.
    """
    now = timezone.now()
    hours_before = getattr(settings, 'REMINDER_HOURS_BEFORE', 3)
    
    # Fenêtre de temps: maintenant + (X-0.25)h à maintenant + (X+0.25)h
    # (pour couvrir les 30 minutes entre deux exécutions)
    time_min = now + timedelta(hours=hours_before - 0.25)
    time_max = now + timedelta(hours=hours_before + 0.25)
    
    # Rechercher les tâches non terminées avec une heure définie
    # dont l'échéance tombe dans la fenêtre de temps
    # et pour lesquelles le rappel n'a pas encore été envoyé
    tasks = Task.objects.filter(
        due_date=time_min.date(),  # Même date que la fenêtre
        due_time__isnull=False,  # Doit avoir une heure définie
        status__in=[Task.TaskStatus.PENDING, Task.TaskStatus.IN_PROGRESS],
        reminder_hours_sent=False
    ).select_related('assigned_to', 'assigned_by', 'related_installation')
    
    # Filtrer plus finement avec la combinaison date+heure
    tasks_to_remind = []
    for task in tasks:
        # Construire datetime complet de l'échéance
        task_datetime = timezone.make_aware(
            timezone.datetime.combine(task.due_date, task.due_time)
        )
        
        # Vérifier si dans la fenêtre
        if time_min <= task_datetime <= time_max:
            tasks_to_remind.append(task)
    
    sent_count = 0
    failed_count = 0
    
    for task in tasks_to_remind:
        try:
            # Vérifier que l'utilisateur assigné a un email
            if not task.assigned_to.email:
                print(f"[Rappel {hours_before}h] Tâche {task.id}: utilisateur sans email")
                continue
            
            # Calculer les heures restantes pour affichage
            task_datetime = timezone.make_aware(
                timezone.datetime.combine(task.due_date, task.due_time)
            )
            hours_remaining = round((task_datetime - now).total_seconds() / 3600, 1)
            
            # Préparer le contexte pour le template
            context = {
                'task': task,
                'hours_remaining': int(hours_remaining),
                'frontend_url': '',  # Sera rempli par email_utils
            }
            
            # Envoyer l'email (sans emoji dans le sujet)
            success, message = send_mail(
                template='emails/planning/task_reminder_hours.html',
                context=context,
                subject=f"Rappel urgent : {task.title} - Dans {int(hours_remaining)}h",
                to=task.assigned_to.email,
                save_to_log=True,
            )
            
            if success:
                # Marquer le rappel comme envoyé
                task.reminder_hours_sent = True
                task.save(update_fields=['reminder_hours_sent'])
                sent_count += 1
                print(f"[Rappel {hours_before}h] Envoyé pour tâche {task.id} à {task.assigned_to.email}")
            else:
                failed_count += 1
                print(f"[Rappel {hours_before}h] Échec pour tâche {task.id}: {message}")
                
        except Exception as e:
            failed_count += 1
            print(f"[Rappel {hours_before}h] Erreur pour tâche {task.id}: {e}")
    
    print(f"[Rappel {hours_before}h] Résumé: {sent_count} envoyés, {failed_count} échecs")
    return {'sent': sent_count, 'failed': failed_count}


@shared_task(name='planning.tasks.send_deadline_notification')
def send_deadline_notification():
    """
    Envoie une notification au créateur de la tâche lorsque l'échéance est atteinte.
    L'heure par défaut pour les tâches sans heure est configurable via REMINDER_TIME_HOUR.
    Exécuté toutes les 15 minutes pour vérifier les échéances.
    """
    now = timezone.now()
    default_reminder_hour = getattr(settings, 'REMINDER_TIME_HOUR', 8)
    
    # Fenêtre de temps: maintenant - 15 min à maintenant + 15 min
    time_min = now - timedelta(minutes=15)
    time_max = now + timedelta(minutes=15)
    
    # Rechercher les tâches dont l'échéance est dans la fenêtre
    # et pour lesquelles la notification n'a pas encore été envoyée
    tasks = Task.objects.filter(
        due_date=now.date(),  # Échéance aujourd'hui
        status__in=[Task.TaskStatus.PENDING, Task.TaskStatus.IN_PROGRESS, Task.TaskStatus.COMPLETED],
        reminder_deadline_sent=False,
        assigned_by__isnull=False  # Doit avoir un créateur
    ).select_related('assigned_to', 'assigned_by', 'related_installation')
    
    # Filtrer selon l'heure (si définie)
    tasks_to_notify = []
    for task in tasks:
        if task.due_time:
            # Tâche avec heure spécifique
            task_datetime = timezone.make_aware(
                timezone.datetime.combine(task.due_date, task.due_time)
            )
            if time_min <= task_datetime <= time_max:
                tasks_to_notify.append(task)
        else:
            # Tâche sans heure: notifier à l'heure configurée le jour J
            target_time = timezone.make_aware(
                timezone.datetime.combine(task.due_date, timezone.datetime.min.time().replace(hour=default_reminder_hour))
            )
            if time_min <= target_time <= time_max:
                tasks_to_notify.append(task)
    
    sent_count = 0
    failed_count = 0
    
    for task in tasks_to_notify:
        try:
            # Vérifier que le créateur a un email
            if not task.assigned_by or not task.assigned_by.email:
                print(f"[Notif échéance] Tâche {task.id}: créateur sans email")
                # Marquer quand même comme notifié pour éviter de ressayer
                task.reminder_deadline_sent = True
                task.save(update_fields=['reminder_deadline_sent'])
                continue
            
            # Préparer le contexte pour le template
            context = {
                'task': task,
                'frontend_url': '',  # Sera rempli par email_utils
            }
            
            # Envoyer l'email (sans emoji dans le sujet)
            success, message = send_mail(
                template='emails/planning/task_deadline_notice.html',
                context=context,
                subject=f"Échéance atteinte : {task.title}",
                to=task.assigned_by.email,
                save_to_log=True,
            )
            
            if success:
                # Marquer la notification comme envoyée
                task.reminder_deadline_sent = True
                task.save(update_fields=['reminder_deadline_sent'])
                sent_count += 1
                print(f"[Notif échéance] Envoyé pour tâche {task.id} à {task.assigned_by.email}")
            else:
                failed_count += 1
                print(f"[Notif échéance] Échec pour tâche {task.id}: {message}")
                
        except Exception as e:
            failed_count += 1
            print(f"[Notif échéance] Erreur pour tâche {task.id}: {e}")
    
    print(f"[Notif échéance] Résumé: {sent_count} envoyés, {failed_count} échecs")
    return {'sent': sent_count, 'failed': failed_count}
