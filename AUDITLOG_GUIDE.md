# Guide complet : django-auditlog pour EuropGreen Solar

## 📚 Vue d'ensemble

**django-auditlog** est maintenant configuré et actif sur le projet. Il trace **automatiquement** toutes les modifications (CREATE, UPDATE, DELETE) sur les modèles enregistrés.

### ✅ Configuration actuelle

- ✅ Package installé : `django-auditlog==3.0.0`
- ✅ Middleware activé : `AuditlogMiddleware`
- ✅ 28 modèles enregistrés (User, ProspectRequest, Offer, Quote, Invoice, etc.)
- ✅ Migrations appliquées : table `auditlog_logentry` créée

---

## 🗂️ Structure de la table `auditlog_logentry`

Chaque modification enregistre :

| Champ | Description |
|-------|-------------|
| `id` | ID unique du log |
| `content_type` | Type de modèle (ex: `request.prospectrequest`) |
| `object_pk` | Clé primaire de l'objet modifié |
| `object_repr` | Représentation string de l'objet (`__str__`) |
| `action` | Type d'action : `0=CREATE`, `1=UPDATE`, `2=DELETE`, `3=ACCESS` |
| `changes` | JSONField avec les changements `{"champ": ["old_value", "new_value"]}` |
| `timestamp` | Date/heure de l'action |
| `actor` | ForeignKey vers User (qui a fait l'action) |
| `remote_addr` | Adresse IP de l'utilisateur |
| `additional_data` | JSONField pour métadonnées supplémentaires |
| `serialized_data` | JSONField avec snapshot complet de l'objet |

---

## 🔍 Exemples d'utilisation

### 1. Récupérer l'historique d'un objet spécifique

```python
from auditlog.models import LogEntry
from request.models import ProspectRequest

# Récupérer l'historique d'une demande spécifique
request = ProspectRequest.objects.get(id='...')
history = LogEntry.objects.get_for_object(request)

for log in history:
    print(f"{log.timestamp} - {log.actor} - {log.get_action_display()}")
    print(f"Changements: {log.changes}")
```

### 2. Récupérer l'historique d'un utilisateur (client)

```python
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from users.models import User

# Historique d'un user spécifique
user = User.objects.get(email='client@example.com')
user_ct = ContentType.objects.get_for_model(User)

# Logs où cet user est l'objet modifié
logs_as_object = LogEntry.objects.filter(
    content_type=user_ct,
    object_pk=str(user.pk)
)

# Logs où cet user a effectué des actions
logs_as_actor = LogEntry.objects.filter(actor=user)
```

### 3. Récupérer toutes les actions d'un client (demandes, offres, devis, etc.)

```python
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from users.models import User
from request.models import ProspectRequest
from offers.models import Offer
from billing.models import Quote

user = User.objects.get(email='client@example.com')

# 1. Logs du user lui-même
user_ct = ContentType.objects.get_for_model(User)
user_logs = LogEntry.objects.filter(content_type=user_ct, object_pk=str(user.pk))

# 2. Logs des demandes liées au user
requests = ProspectRequest.objects.filter(source=user)
request_ct = ContentType.objects.get_for_model(ProspectRequest)
request_logs = LogEntry.objects.filter(
    content_type=request_ct,
    object_pk__in=[str(r.pk) for r in requests]
)

# 3. Logs des offres liées
offers = Offer.objects.filter(request__source=user)
offer_ct = ContentType.objects.get_for_model(Offer)
offer_logs = LogEntry.objects.filter(
    content_type=offer_ct,
    object_pk__in=[str(o.pk) for o in offers]
)

# Combiner tous les logs
all_logs = (user_logs | request_logs | offer_logs).order_by('-timestamp')
```

### 4. Timeline d'un client (format API)

```python
def get_client_timeline(user):
    """Retourne la timeline complète d'un client"""
    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    
    # Content types
    user_ct = ContentType.objects.get_for_model(User)
    request_ct = ContentType.objects.get_for_model(ProspectRequest)
    offer_ct = ContentType.objects.get_for_model(Offer)
    quote_ct = ContentType.objects.get_for_model(Quote)
    
    # Récupérer tous les objets liés
    requests = ProspectRequest.objects.filter(source=user)
    offers = Offer.objects.filter(request__in=requests)
    quotes = Quote.objects.filter(offer__in=offers)
    
    # Construire la requête de logs
    logs = LogEntry.objects.filter(
        models.Q(content_type=user_ct, object_pk=str(user.pk)) |
        models.Q(content_type=request_ct, object_pk__in=[str(r.pk) for r in requests]) |
        models.Q(content_type=offer_ct, object_pk__in=[str(o.pk) for o in offers]) |
        models.Q(content_type=quote_ct, object_pk__in=[str(q.pk) for q in quotes])
    ).select_related('actor', 'content_type').order_by('-timestamp')
    
    # Formater pour l'API
    timeline = []
    for log in logs:
        timeline.append({
            'id': log.id,
            'timestamp': log.timestamp,
            'action': log.get_action_display(),
            'action_code': log.action,  # 0=CREATE, 1=UPDATE, 2=DELETE
            'object_type': log.content_type.model,
            'object_repr': log.object_repr,
            'actor': {
                'id': log.actor.id if log.actor else None,
                'name': log.actor.get_full_name() if log.actor else 'Système',
                'email': log.actor.email if log.actor else None,
            },
            'changes': log.changes,
            'remote_addr': log.remote_addr,
        })
    
    return timeline
```

---

## 🎨 Créer un ViewSet pour exposer l'historique via API

### Étape 1 : Créer un serializer

**Fichier:** `back/admin_platform/serializers.py`

```python
from rest_framework import serializers
from auditlog.models import LogEntry

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    actor_email = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    object_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = LogEntry
        fields = [
            'id', 'timestamp', 'action', 'action_display',
            'object_type', 'object_repr', 'object_pk',
            'changes', 'actor_name', 'actor_email', 'remote_addr',
            'additional_data'
        ]
    
    def get_actor_name(self, obj):
        if obj.actor:
            return obj.actor.get_full_name()
        return 'Système'
    
    def get_actor_email(self, obj):
        return obj.actor.email if obj.actor else None
```

### Étape 2 : Créer un ViewSet

**Fichier:** `back/admin_platform/views.py`

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from users.models import User
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les logs d'audit.
    
    Query params:
    - user_id: Filter par utilisateur (objet ou acteur)
    - model: Filter par type de modèle (ex: prospectrequest, offer)
    - action: Filter par action (0=CREATE, 1=UPDATE, 2=DELETE)
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
        
        # Filter par user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            # Logs où le user est l'objet OU l'acteur
            user_ct = ContentType.objects.get_for_model(User)
            queryset = queryset.filter(
                models.Q(content_type=user_ct, object_pk=user_id) |
                models.Q(actor_id=user_id)
            )
        
        # Filter par type de modèle
        model_name = self.request.query_params.get('model')
        if model_name:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                pass
        
        # Filter par action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='user-timeline/(?P<user_id>[^/.]+)')
    def user_timeline(self, request, user_id=None):
        """
        Timeline complète d'un utilisateur (user + demandes + offres + devis + etc.)
        
        GET /api/admin-platform/audit-logs/user-timeline/{user_id}/
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        # Content types
        user_ct = ContentType.objects.get_for_model(User)
        request_ct = ContentType.objects.get_for_model(ProspectRequest)
        offer_ct = ContentType.objects.get_for_model(Offer)
        quote_ct = ContentType.objects.get_for_model(Quote)
        
        # Objets liés
        from request.models import ProspectRequest
        from offers.models import Offer
        from billing.models import Quote
        
        requests = ProspectRequest.objects.filter(source=user)
        offers = Offer.objects.filter(request__in=requests)
        quotes = Quote.objects.filter(offer__in=offers)
        
        # Logs combinés
        logs = LogEntry.objects.filter(
            models.Q(content_type=user_ct, object_pk=str(user.pk)) |
            models.Q(content_type=request_ct, object_pk__in=[str(r.pk) for r in requests]) |
            models.Q(content_type=offer_ct, object_pk__in=[str(o.pk) for o in offers]) |
            models.Q(content_type=quote_ct, object_pk__in=[str(q.pk) for q in quotes])
        ).select_related('actor', 'content_type').order_by('-timestamp')
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
```

### Étape 3 : Enregistrer les routes

**Fichier:** `back/admin_platform/urls.py`

```python
from rest_framework.routers import DefaultRouter
from .views import EmailLogViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'email-logs', EmailLogViewSet, basename='email-log')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = router.urls
```

---

## 🌐 Utilisation Frontend

### Exemple : Récupérer la timeline d'un user

```typescript
// Récupérer tous les logs d'un user
const logs = await $fetch(`/api/admin-platform/audit-logs/?user_id=${userId}`, {
  credentials: 'include'
})

// Récupérer la timeline complète (user + demandes + offres...)
const timeline = await $fetch(`/api/admin-platform/audit-logs/user-timeline/${userId}/`, {
  credentials: 'include'
})
```

### Exemple de rendu timeline (Vue)

```vue
<template>
  <div class="timeline">
    <div v-for="log in timeline" :key="log.id" class="timeline-item">
      <div class="timeline-marker" :class="getActionClass(log.action_code)" />
      <div class="timeline-content">
        <div class="flex justify-between items-start">
          <div>
            <span class="font-semibold">{{ log.action_display }}</span>
            <span class="text-gray-600 ml-2">{{ log.object_type }}</span>
          </div>
          <span class="text-sm text-gray-500">
            {{ formatDate(log.timestamp) }}
          </span>
        </div>
        <p class="text-sm text-gray-700 mt-1">{{ log.object_repr }}</p>
        <div v-if="log.changes && Object.keys(log.changes).length" class="mt-2">
          <details class="text-xs">
            <summary class="cursor-pointer text-gray-600">Voir les changements</summary>
            <pre class="mt-2 p-2 bg-gray-50 rounded">{{ JSON.stringify(log.changes, null, 2) }}</pre>
          </details>
        </div>
        <p class="text-xs text-gray-500 mt-2">
          Par {{ log.actor_name }} ({{ log.actor_email }})
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
function getActionClass(action) {
  // 0=CREATE, 1=UPDATE, 2=DELETE
  const classes = {
    0: 'bg-green-500',
    1: 'bg-blue-500',
    2: 'bg-red-500',
  }
  return classes[action] || 'bg-gray-500'
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString('fr-FR')
}
</script>
```

---

## ⚙️ Options avancées

### Exclure certains champs du logging

```python
# Dans auditlog_registry.py
auditlog.register(
    User,
    exclude_fields=['password', 'last_login', 'session_data']
)
```

### Logger les relations many-to-many

```python
auditlog.register(
    User,
    m2m_fields=['groups', 'user_permissions']
)
```

### Désactiver temporairement l'audit

```python
from auditlog.context import disable_auditlog

with disable_auditlog():
    # Les modifications ici ne seront PAS loggées
    user.save()
```

### Ajouter des métadonnées custom

```python
from auditlog.context import set_additional_data

set_additional_data(
    triggered_by='api_endpoint',
    reason='user_requested_change',
    metadata={'foo': 'bar'}
)
user.save()  # Le log contiendra ces métadonnées dans additional_data
```

---

## 📊 Requêtes utiles

### Statistiques d'activité

```python
from auditlog.models import LogEntry
from django.db.models import Count

# Nombre d'actions par type
stats = LogEntry.objects.values('action').annotate(count=Count('id'))

# Top 10 users les plus actifs
top_users = LogEntry.objects.filter(actor__isnull=False)\
    .values('actor__email')\
    .annotate(count=Count('id'))\
    .order_by('-count')[:10]

# Actions récentes (dernières 24h)
from django.utils import timezone
from datetime import timedelta

recent = LogEntry.objects.filter(
    timestamp__gte=timezone.now() - timedelta(hours=24)
)
```

### Recherche d'un changement spécifique

```python
# Trouver tous les logs où le statut d'une demande a changé
logs = LogEntry.objects.filter(
    content_type__model='prospectrequest',
    changes__has_key='status'
)

# Trouver tous les emails modifiés
logs = LogEntry.objects.filter(
    changes__has_key='email'
)
```

---

## 🚀 Prochaines étapes

1. **Créer le ViewSet** `AuditLogViewSet` dans `admin_platform/views.py`
2. **Ajouter les routes** dans `admin_platform/urls.py`
3. **Créer une page frontend** `/home/user-history/:id` avec timeline
4. **Intégrer dans la fiche client** : bouton "Voir l'historique complet"

---

## 📝 Notes importantes

- ✅ Les logs sont créés **automatiquement** à chaque save/delete
- ✅ Le middleware capture le `request.user` et l'IP
- ✅ Les données sont en JSON (facile à parser)
- ✅ Pas besoin de modifier le code existant
- ⚠️ La table peut grossir vite : prévoir un archivage/nettoyage périodique
- ⚠️ Ne pas logger les champs sensibles (password, tokens, etc.)

---

## 🔗 Ressources

- Documentation officielle : https://django-auditlog.readthedocs.io/
- GitHub : https://github.com/jazzband/django-auditlog
- Fichier config projet : `back/EuropGreenSolar/auditlog_registry.py`
