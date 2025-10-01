from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'assigned_to', 'assigned_by', 'due_date', 
        'status', 'priority', 'created_at'
    ]
    list_filter = ['status', 'priority', 'due_date', 'created_at']
    search_fields = ['title', 'description', 'assigned_to__email', 'assigned_by__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'description', 'priority')
        }),
        ('Assignation', {
            'fields': ('assigned_to', 'assigned_by', 'related_installation')
        }),
        ('Dates et statut', {
            'fields': ('due_date', 'due_time', 'status', 'completed_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
