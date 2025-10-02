# Système de logs d'emails - Documentation

## Ce qui a été ajouté

### 1. Nouvelle application `admin_platform`
- Modèle `EmailLog` pour enregistrer les emails envoyés
- Configuration admin Django basique (optionnelle)

### 2. Modification de `email_utils.py`
- Nouveau paramètre `save_to_log=True` dans la fonction `send_mail()`
- Enregistrement automatique des emails envoyés dans `EmailLog`
- Les emails ne sont enregistrés QUE si l'envoi réussit

### 3. Protection des données sensibles
- Email avec mot de passe dans `installations/views.py` : `save_to_log=False` ✅
- Emails d'authentification dans `users/serializers.py` et `authentication/serializers.py` utilisent l'ancienne méthode Django (pas notre utilitaire, donc pas enregistrés)

## Champs enregistrés dans EmailLog

- `recipients` : Liste des destinataires
- `subject` : Sujet
- `html_content` : Contenu HTML complet
- `plain_content` : Version texte
- `from_email` : Expéditeur
- `template_used` : Template utilisé
- `send_method` : "mailgun" ou "smtp"
- `sent_at` : Date/heure d'envoi
- `attachments_info` : Liste des pièces jointes (noms et types MIME)

**Note** : Le contenu des pièces jointes n'est PAS stocké.

## Utilisation

### Email normal (enregistré)
```python
from EuropGreenSolar.email_utils import send_mail

send_mail(
    template='emails/prospect/prospect_assigned.html',
    context={'prospect': prospect},
    subject='Nouvelle demande',
    to='user@example.com',
)
```

### Email sensible (NON enregistré)
```python
send_mail(
    template='emails/installation/installation_started.html',
    context={'password': 'secret123'},
    subject='Vos identifiants',
    to='user@example.com',
    save_to_log=False,  # ← Important !
)
```

## Fichiers modifiés

- ✅ `back/EuropGreenSolar/settings.py` : Ajout de `admin_platform` dans `INSTALLED_APPS`
- ✅ `back/EuropGreenSolar/email_utils.py` : Ajout du paramètre `save_to_log` et logique d'enregistrement
- ✅ `back/admin_platform/models.py` : Modèle `EmailLog`
- ✅ `back/admin_platform/admin.py` : Configuration admin basique
- ✅ `back/admin_platform/migrations/0001_initial.py` : Migration
- ✅ `back/installations/views.py` : Ajout de `save_to_log=False` pour l'email avec mot de passe

## Notes importantes

- Les emails envoyés via l'ancienne méthode Django (`django.core.mail.send_mail`) dans `users/serializers.py` et `authentication/serializers.py` ne sont PAS enregistrés (ce qui est bien pour la sécurité)
- Seuls les emails envoyés via `EuropGreenSolar.email_utils.send_mail` sont enregistrés
- L'interface admin Django est disponible mais optionnelle
