from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Task(models.Model):
    """
    Modèle pour la gestion des tâches et planification.
    Permet d'assigner des tâches spécifiques aux membres de l'équipe.
    """

    class TaskStatus(models.TextChoices):
        PENDING = "pending", "En attente"
        IN_PROGRESS = "in_progress", "En cours"
        COMPLETED = "completed", "Terminée"
        CANCELLED = "cancelled", "Annulée"

    class TaskPriority(models.TextChoices):
        LOW = "low", "Basse"
        NORMAL = "normal", "Normale"
        HIGH = "high", "Haute"
        URGENT = "urgent", "Urgente"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Assignation
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
        verbose_name="Assigné à"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        verbose_name="Créé par"
    )
    
    # Dates et statut
    due_date = models.DateField(verbose_name="Date d'échéance")
    due_time = models.TimeField(null=True, blank=True, verbose_name="Heure d'échéance")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.NORMAL,
        verbose_name="Priorité"
    )
    
    # Relation optionnelle avec une installation
    related_installation = models.ForeignKey(
        "installations.Form",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Installation liée"
    )
    
    # Métadonnées
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Terminée le")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")
    
    # Notes additionnelles
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        ordering = ['-due_date', '-priority']
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        indexes = [
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        assigned_name = self.assigned_to.get_full_name() if self.assigned_to else "Non assigné"
        return f"{self.title} - {assigned_name} - {self.due_date.strftime('%d/%m/%Y')}"

    def mark_as_completed(self):
        """Marque la tâche comme terminée."""
        self.status = self.TaskStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def is_overdue(self):
        """Vérifie si la tâche est en retard."""
        if self.status in [self.TaskStatus.COMPLETED, self.TaskStatus.CANCELLED]:
            return False
        return self.due_date < timezone.now().date()

    @property
    def assigned_to_name(self):
        """Retourne le nom complet de la personne assignée."""
        return f"{self.assigned_to.first_name} {self.assigned_to.last_name}".strip()

    @property
    def assigned_by_name(self):
        """Retourne le nom complet du créateur."""
        if self.assigned_by:
            return f"{self.assigned_by.first_name} {self.assigned_by.last_name}".strip()
        return "Système"
