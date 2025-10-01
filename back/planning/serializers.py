from rest_framework import serializers
from .models import Task
from users.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Serializer de base pour les tâches."""
    
    assigned_to_name = serializers.ReadOnlyField()
    assigned_by_name = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    # Informations simplifiées de l'utilisateur assigné
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    assigned_by_detail = UserSerializer(source='assigned_by', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_by',
            'assigned_to_name', 'assigned_by_name', 'assigned_to_detail', 'assigned_by_detail',
            'due_date', 'due_time', 'status', 'priority',
            'related_installation', 'completed_at', 'created_at', 'updated_at',
            'notes', 'is_overdue'
        ]
        read_only_fields = ['id', 'assigned_by', 'completed_at', 'created_at', 'updated_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une tâche individuelle."""
    
    assigned_to_name = serializers.ReadOnlyField()
    assigned_by_name = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    
    # Informations complètes des utilisateurs
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    assigned_by_detail = UserSerializer(source='assigned_by', read_only=True)
    
    # Informations sur l'installation liée (si applicable)
    installation_details = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'assigned_by',
            'assigned_to_name', 'assigned_by_name', 'assigned_to_detail', 'assigned_by_detail',
            'due_date', 'due_time', 'status', 'priority',
            'related_installation', 'installation_details', 
            'completed_at', 'created_at', 'updated_at',
            'notes', 'is_overdue'
        ]
        read_only_fields = ['id', 'assigned_by', 'completed_at', 'created_at', 'updated_at']

    def get_installation_details(self, obj):
        """Retourne les informations de base de l'installation liée."""
        if obj.related_installation:
            return {
                'id': str(obj.related_installation.id),
                'client_name': f"{obj.related_installation.offer.first_name} {obj.related_installation.offer.last_name}",
                'status': obj.related_installation.status,
            }
        return None


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de tâche."""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assigned_to', 'due_date', 'due_time',
            'priority', 'related_installation', 'notes'
        ]

    def validate_due_date(self, value):
        """Valide que la date d'échéance n'est pas dans le passé."""
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("La date d'échéance ne peut pas être dans le passé.")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour de tâche."""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'due_date', 'due_time',
            'status', 'priority', 'notes'
        ]

    def validate(self, data):
        """Valide les données de mise à jour."""
        # Si le statut passe à "completed", on enregistre la date de complétion
        if data.get('status') == Task.TaskStatus.COMPLETED and self.instance.status != Task.TaskStatus.COMPLETED:
            from django.utils import timezone
            data['completed_at'] = timezone.now()
        return data
