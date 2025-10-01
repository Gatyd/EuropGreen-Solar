from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Task
from .serializers import (
    TaskSerializer, TaskDetailSerializer, 
    TaskCreateSerializer, TaskUpdateSerializer
)
from authentication.permissions import IsAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tâches.
    
    Permissions:
    - Admins : peuvent créer, modifier, supprimer toutes les tâches
    - Staff : peuvent voir leurs tâches assignées et les marquer comme terminées
    - Clients : aucun accès
    """
    queryset = Task.objects.select_related(
        'assigned_to', 'assigned_by', 'related_installation'
    ).all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def get_permissions(self):
        """
        Permissions personnalisées selon l'action.
        """
        user = getattr(self.request, 'user', None)
        action = getattr(self, 'action', None)
        
        # Seuls les admins peuvent créer et supprimer des tâches
        if action in ['create', 'destroy']:
            return [IsAdmin()]
        
        # Les staff peuvent voir et modifier (partiellement) leurs tâches
        if action in ['list', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """
        Filtre les tâches selon l'utilisateur :
        - Admins : toutes les tâches
        - Staff : uniquement leurs tâches assignées
        - Clients : aucune tâche
        """
        user = self.request.user
        
        if not user.is_authenticated:
            return Task.objects.none()
        
        # Admins voient tout
        if user.is_superuser:
            qs = Task.objects.all()
        # Staff voient leurs tâches ou celles qu'ils ont créées
        elif user.is_staff:
            qs = Task.objects.filter(
                Q(assigned_to=user) | Q(assigned_by=user)
            )
        else:
            # Les clients n'ont pas accès
            return Task.objects.none()
        
        # Filtres optionnels via query params
        params = self.request.query_params
        
        # Filtre par statut
        status_param = params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        
        # Filtre par priorité
        priority_param = params.get('priority')
        if priority_param:
            qs = qs.filter(priority=priority_param)
        
        # Filtre par utilisateur assigné (admin uniquement)
        if user.is_superuser:
            assigned_to_param = params.get('assigned_to')
            if assigned_to_param:
                qs = qs.filter(assigned_to_id=assigned_to_param)
        
        # Filtre par mois (pour le calendrier)
        month_param = params.get('month')  # Format: YYYY-MM
        if month_param:
            try:
                year, month = map(int, month_param.split('-'))
                qs = qs.filter(due_date__year=year, due_date__month=month)
            except (ValueError, AttributeError):
                pass
        
        # Filtre par installation
        installation_param = params.get('installation')
        if installation_param:
            qs = qs.filter(related_installation_id=installation_param)
        
        return qs.select_related('assigned_to', 'assigned_by', 'related_installation')

    def perform_create(self, serializer):
        """Enregistre le créateur de la tâche et envoie un email de notification."""
        task = serializer.save(assigned_by=self.request.user)
        
        # Envoi de l'email de notification après commit
        from django.db import transaction
        transaction.on_commit(lambda: self._send_task_assignment_email(task))

    def perform_update(self, serializer):
        """
        Vérifie les permissions avant mise à jour.
        Les staff ne peuvent modifier que certains champs de leurs propres tâches.
        """
        user = self.request.user
        task = self.get_object()
        
        # Si pas admin et pas assigné à cette tâche, refuser
        if not user.is_superuser and task.assigned_to != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous ne pouvez modifier que vos propres tâches.")
        
        # Si staff (non admin), limiter les champs modifiables
        if not user.is_superuser and user.is_staff:
            allowed_fields = {'status', 'notes'}
            request_fields = set(self.request.data.keys())
            if not request_fields.issubset(allowed_fields):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Vous ne pouvez modifier que le statut et les notes.")
        
        serializer.save()

    def _send_task_assignment_email(self, task: Task):
        """Envoie un email de notification à la personne assignée."""
        try:
            from EuropGreenSolar.email_utils import send_mail
            
            context = {
                'task': task,
                'assigned_to': task.assigned_to,
                'assigned_by': task.assigned_by,
                'frontend_url': getattr(self.request, 'META', {}).get('HTTP_ORIGIN', 'http://localhost:3000'),
            }
            
            send_mail(
                template='emails/planning/task_assigned.html',
                context=context,
                subject=f"Nouvelle tâche assignée : {task.title}",
                to=task.assigned_to.email,
            )
        except Exception as e:
            # Log l'erreur mais ne bloque pas la création
            print(f"Erreur lors de l'envoi de l'email de notification : {e}")

    @action(detail=True, methods=['post'], url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        """Marque une tâche comme terminée."""
        task = self.get_object()
        
        # Vérifier les permissions
        if not request.user.is_superuser and task.assigned_to != request.user:
            return Response(
                {'detail': 'Vous ne pouvez marquer comme terminée que vos propres tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.mark_as_completed()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='my-tasks')
    def my_tasks(self, request):
        """Retourne les tâches de l'utilisateur courant."""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue_tasks(self, request):
        """Retourne les tâches en retard."""
        today = timezone.now().date()
        tasks = self.get_queryset().filter(
            due_date__lt=today,
            status__in=[Task.TaskStatus.PENDING, Task.TaskStatus.IN_PROGRESS]
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='upcoming')
    def upcoming_tasks(self, request):
        """Retourne les tâches à venir dans les 7 prochains jours."""
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        tasks = self.get_queryset().filter(
            due_date__gte=today,
            due_date__lte=next_week,
            status__in=[Task.TaskStatus.PENDING, Task.TaskStatus.IN_PROGRESS]
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
