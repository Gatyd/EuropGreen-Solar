# Système de Rappels pour les Tâches - Documentation

## Vue d'ensemble

Le système de rappels automatiques envoie des notifications email aux utilisateurs pour les aider à gérer leurs tâches efficacement. Il utilise **Celery** avec **Redis** comme broker de messages et **Celery Beat** pour l'ordonnancement.

---

## Architecture

### Composants

1. **Redis** : Broker de messages pour Celery
2. **Celery Worker** : Exécute les tâches asynchrones
3. **Celery Beat** : Scheduler pour les tâches périodiques
4. **Django** : Application web principale

### Services Docker

- `redis` : Serveur Redis (port 6379)
- `celery-worker` : Worker Celery pour exécuter les tâches
- `celery-beat` : Scheduler Celery Beat pour les tâches planifiées
- `web` : Application Django principale

---

## Types de Rappels

### 1. Rappel 3 jours avant (08h00)

**Destinataire** : Utilisateur assigné (`assigned_to`)

**Timing** : Tous les jours à 08h00 (heure de Paris)

**Conditions** :
- Tâche à venir dans exactement 3 jours
- Statut : `pending` ou `in_progress`
- `reminder_3days_sent = False`

**Template** : `emails/planning/task_reminder_3_days.html`

### 2. Rappel 3 heures avant

**Destinataire** : Utilisateur assigné (`assigned_to`)

**Timing** : Toutes les 30 minutes (vérifie fenêtre de 2h45 à 3h15)

**Conditions** :
- Tâche avec `due_time` définie
- Échéance dans 3 heures (±15 min)
- Statut : `pending` ou `in_progress`
- `reminder_hours_sent = False`

**Template** : `emails/planning/task_reminder_hours.html`

### 3. Notification à l'échéance

**Destinataire** : Créateur de la tâche (`assigned_by`)

**Timing** : Toutes les 15 minutes (vérifie fenêtre de ±15 min)

**Conditions** :
- Échéance atteinte (date + heure si définie)
- Statut : tous (même `completed` pour information)
- `reminder_deadline_sent = False`
- `assigned_by` existe

**Template** : `emails/planning/task_deadline_notice.html`

**Note** : Pour les tâches sans heure, la notification est envoyée à 08h00 le jour J.

---

## Configuration

### Variables d'environnement (.env)

```env
# Celery & Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email (pour l'envoi des rappels)
MAILGUN_API_KEY=your_key
MAILGUN_DOMAIN=your_domain
# ou SMTP
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=user@example.com
EMAIL_HOST_PASSWORD=password
EMAIL_PORT=587
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@example.com

# Frontend URL (pour les liens dans les emails)
FRONTEND_URL=https://your-domain.com
```

### Configuration Celery (settings.py)

```python
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_TIMEZONE = 'Europe/Paris'
CELERY_ENABLE_UTC = False
```

---

## Déploiement

### Développement local

1. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

2. **Appliquer les migrations** :
   ```bash
   python manage.py migrate
   ```

3. **Lancer Redis localement** :
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

4. **Lancer le worker Celery** :
   ```bash
   celery -A EuropGreenSolar worker -l info
   ```

5. **Lancer Celery Beat** :
   ```bash
   celery -A EuropGreenSolar beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

6. **Lancer Django** :
   ```bash
   python manage.py runserver
   ```

### Production (Docker)

1. **Builder et lancer tous les services** :
   ```bash
   docker-compose up -d --build
   ```

2. **Vérifier les logs** :
   ```bash
   # Logs du worker
   docker-compose logs -f celery-worker
   
   # Logs du beat
   docker-compose logs -f celery-beat
   
   # Logs Redis
   docker-compose logs -f redis
   ```

3. **Appliquer les migrations** :
   ```bash
   docker-compose exec web python manage.py migrate
   ```

---

## Surveillance et Debugging

### Vérifier l'état des tâches

```python
# Dans le shell Django
python manage.py shell

from planning.models import Task
from django.utils import timezone

# Tâches éligibles pour rappel 3 jours
tasks_3d = Task.objects.filter(
    due_date=(timezone.now() + timezone.timedelta(days=3)).date(),
    status__in=['pending', 'in_progress'],
    reminder_3days_sent=False
)
print(f"Tâches pour rappel 3j: {tasks_3d.count()}")

# Vérifier les rappels déjà envoyés
sent_reminders = Task.objects.filter(reminder_3days_sent=True).count()
print(f"Rappels 3j envoyés: {sent_reminders}")
```

### Logs Celery

Les tâches logguent leur activité avec des préfixes :
- `[Rappel 3j]` : Rappel 3 jours avant
- `[Rappel 3h]` : Rappel 3 heures avant
- `[Notif échéance]` : Notification à l'échéance

### Tester manuellement une tâche

```python
from planning.tasks import send_reminder_3_days_before

# Exécuter immédiatement (synchrone - pour debug)
result = send_reminder_3_days_before()
print(result)  # {'sent': X, 'failed': Y}

# Exécuter via Celery (asynchrone)
task = send_reminder_3_days_before.delay()
print(task.id)  # ID de la tâche
```

---

## Modèle de données

### Nouveaux champs dans `Task`

```python
reminder_3days_sent = models.BooleanField(default=False)
reminder_hours_sent = models.BooleanField(default=False)
reminder_deadline_sent = models.BooleanField(default=False)
```

**Objectif** : Éviter d'envoyer plusieurs fois le même rappel

**Reset** : Ces champs ne sont **jamais** réinitialisés automatiquement. Si vous modifiez la date d'échéance d'une tâche et souhaitez renvoyer les rappels, vous devez les remettre à `False` manuellement.

---

## Optimisations implémentées

### 1. Requêtes optimisées
- `select_related()` pour éviter les requêtes N+1
- Filtres au niveau base de données avant traitement Python
- Index sur `due_date` et `status` (définis dans le modèle)

### 2. Fenêtres temporelles
- Rappel 3h : fenêtre de 30 minutes (2h45 - 3h15) pour gérer l'intervalle d'exécution
- Notification échéance : fenêtre de 30 minutes (±15 min) pour précision

### 3. Gestion des erreurs
- Try/catch autour de chaque envoi d'email
- Compteurs de succès/échecs
- Logs détaillés pour debugging

### 4. Timezone
- Configuration : `Europe/Paris`
- `USE_TZ = True` dans Django
- `timezone.make_aware()` pour les datetime construites

---

## Personnalisation

### Modifier les horaires

Dans `back/EuropGreenSolar/celery.py` :

```python
app.conf.beat_schedule = {
    'send-reminder-3-days-before': {
        'task': 'planning.tasks.send_reminder_3_days_before',
        'schedule': crontab(hour=8, minute=0),  # Modifier l'heure ici
    },
    # ...
}
```

### Modifier la fenêtre de rappel

Dans `back/planning/tasks.py`, fonction `send_reminder_3_hours_before()` :

```python
# Changer de 3h à 2h par exemple
time_min = now + timedelta(hours=1, minutes=45)  # 2h - 15min
time_max = now + timedelta(hours=2, minutes=15)  # 2h + 15min
```

### Ajouter un nouveau type de rappel

1. Créer le template email dans `templates/emails/planning/`
2. Ajouter un champ `reminder_xxx_sent` dans le modèle `Task`
3. Créer la fonction dans `planning/tasks.py`
4. Ajouter l'entrée dans `celery.py` → `beat_schedule`

---

## Troubleshooting

### Les rappels ne sont pas envoyés

1. **Vérifier que Celery Beat tourne** :
   ```bash
   docker-compose ps celery-beat
   ```

2. **Vérifier les logs** :
   ```bash
   docker-compose logs celery-beat
   ```

3. **Vérifier la configuration timezone** :
   ```python
   # Dans settings.py
   TIME_ZONE = 'Europe/Paris'
   USE_TZ = True
   
   # Dans celery.py
   CELERY_TIMEZONE = 'Europe/Paris'
   ```

4. **Vérifier les tâches éligibles** :
   Utiliser le shell Django pour compter les tâches concernées

### Redis n'est pas accessible

```bash
# Tester la connexion
docker-compose exec web python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

### Les emails ne partent pas

1. Vérifier la configuration SMTP/Mailgun dans `.env`
2. Vérifier les logs d'envoi : `[Rappel Xj] Échec pour tâche ...`
3. Tester l'utilitaire email manuellement :
   ```python
   from EuropGreenSolar.email_utils import send_mail
   
   success, msg = send_mail(
       template='emails/planning/task_reminder_3_days.html',
       context={'task': task},
       subject='Test',
       to='test@example.com'
   )
   print(success, msg)
   ```

---

## Maintenance

### Réinitialiser les rappels d'une tâche

```python
task = Task.objects.get(id='...')
task.reminder_3days_sent = False
task.reminder_hours_sent = False
task.reminder_deadline_sent = False
task.save()
```

### Nettoyer les anciennes tâches

Les tâches complétées/annulées ne reçoivent plus de rappels (3j et 3h).
La notification d'échéance peut être envoyée même pour les tâches complétées (pour informer le créateur).

---

## Support

Pour toute question ou problème :
1. Vérifier les logs Celery
2. Tester les tâches manuellement
3. Vérifier la configuration email
4. Consulter la documentation Django Celery : https://docs.celeryq.dev/

---

**Dernière mise à jour** : 13 octobre 2025
