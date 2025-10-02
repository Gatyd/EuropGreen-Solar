"""
Vues pour l'application admin_platform.
"""

from django.db import models
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import EmailLog
from .serializers import EmailLogSerializer


@extend_schema_view(
    list=extend_schema(summary="Liste des logs d'emails", description="Récupère la liste des emails envoyés (réservé aux administrateurs)"),
    retrieve=extend_schema(summary="Détail d'un log d'email", description="Récupère les détails d'un email envoyé"),
)
class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour consulter les logs d'emails.
    Accessible uniquement aux administrateurs.
    """
    
    queryset = EmailLog.objects.all().order_by('-sent_at')
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """
        Filtre les logs selon les paramètres de requête.
        """
        queryset = super().get_queryset()
        
        # Filtre par méthode d'envoi
        send_method = self.request.query_params.get('send_method')
        if send_method:
            queryset = queryset.filter(send_method=send_method)
        
        # Filtre par template
        template = self.request.query_params.get('template')
        if template:
            queryset = queryset.filter(template_used__icontains=template)
        
        # Filtre par date (après)
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(sent_at__gte=date_from)
        
        # Filtre par date (avant)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(sent_at__lte=date_to)
        
        # Recherche dans le sujet
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(subject__icontains=search)
        
        return queryset
    
    @extend_schema(
        summary="Statistiques des emails envoyés",
        description="Retourne des statistiques sur les emails envoyés (total, par méthode, etc.)"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Retourne des statistiques sur les emails envoyés.
        """
        total = EmailLog.objects.count()
        by_method = EmailLog.objects.values('send_method').annotate(
            count=models.Count('id')
        )
        
        return Response({
            'total': total,
            'by_method': {item['send_method']: item['count'] for item in by_method},
        })

