"""
Vues pour l'application admin_platform.
"""

from django.db import models
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from .models import EmailLog
from .serializers import EmailLogSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Liste des logs d'emails", 
        description="Récupère la liste des emails envoyés. Peut être filtré par email du destinataire.",
        parameters=[
            OpenApiParameter(
                name='email',
                description='Adresse email du destinataire pour filtrer les emails',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='send_method',
                description='Méthode d\'envoi (mailgun, smtp)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='search',
                description='Recherche dans le sujet',
                required=False,
                type=str
            ),
        ]
    ),
    retrieve=extend_schema(summary="Détail d'un log d'email", description="Récupère les détails d'un email envoyé"),
)
class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour consulter les logs d'emails.
    
    Permet de :
    - Lister tous les emails envoyés
    - Filtrer par email de destinataire via ?email=adresse@example.com
    - Filtrer par méthode d'envoi
    - Rechercher dans les sujets
    - Voir les détails d'un email spécifique
    """
    
    queryset = EmailLog.objects.all().order_by('-sent_at')
    serializer_class = EmailLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """
        Filtre les logs selon les paramètres de requête.
        """
        queryset = super().get_queryset()
        
        # Filtre par email du destinataire (NOUVEAU - PRIORITAIRE)
        email = self.request.query_params.get('email')
        if email:
            # Pour SQLite : recherche textuelle dans la représentation JSON
            # Pour PostgreSQL : utiliser __contains serait plus optimal mais ceci fonctionne partout
            from django.db.models import Q
            import json
            
            # Recherche dans la représentation JSON en string
            queryset = queryset.filter(
                Q(recipients__icontains=email)  # Recherche textuelle dans le JSON
            )
        
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

