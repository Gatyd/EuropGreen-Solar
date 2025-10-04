"""
Vues pour l'application admin_platform.
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from auditlog.models import LogEntry
from .models import EmailLog
from .serializers import EmailLogSerializer, AuditLogSerializer


class TimelinePagination(PageNumberPagination):
    """
    Pagination spécifique pour la timeline des utilisateurs.
    20 événements par page pour une UX optimale.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


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


@extend_schema_view(
    list=extend_schema(
        summary="Liste des logs d'audit",
        description="Récupère la liste des logs d'audit (modifications des objets).",
        parameters=[
            OpenApiParameter(
                name='user_id',
                description='ID de l\'utilisateur (logs où il est l\'objet ou l\'acteur)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='model',
                description='Nom du modèle (ex: prospectrequest, offer, quote)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='action',
                description='Type d\'action (0=CREATE, 1=UPDATE, 2=DELETE)',
                required=False,
                type=int
            ),
        ]
    ),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour consulter les logs d'audit (django-auditlog).
    
    Permet de :
    - Lister tous les logs d'audit (NON PAGINÉ)
    - Filtrer par utilisateur (objet ou acteur)
    - Filtrer par type de modèle
    - Filtrer par type d'action
    - Récupérer la timeline complète d'un utilisateur (PAGINÉ - 20/page)
    """
    
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Pas de pagination par défaut, uniquement pour user_timeline
    pagination_class = None
    
    def get_queryset(self):
        """Filtre les logs selon les paramètres de requête."""
        queryset = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
        
        # Filtre par user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            from users.models import User
            user_ct = ContentType.objects.get_for_model(User)
            queryset = queryset.filter(
                models.Q(content_type=user_ct, object_pk=user_id) |
                models.Q(actor_id=user_id)
            )
        
        # Filtre par type de modèle
        model_name = self.request.query_params.get('model')
        if model_name:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct)
            except ContentType.DoesNotExist:
                pass
        
        # Filtre par action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset
    
    @extend_schema(
        summary="Timeline complète d'un utilisateur",
        description="Récupère tous les logs liés à un utilisateur : user lui-même, ses demandes, offres, devis, installations, factures, etc. Paginé (20 items par page).",
        parameters=[
            OpenApiParameter(
                name='user_id',
                description='ID de l\'utilisateur',
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='page',
                description='Numéro de page (défaut: 1)',
                required=False,
                type=int,
                location=OpenApiParameter.QUERY
            ),
        ]
    )
    @action(detail=False, methods=['get'], url_path='user-timeline/(?P<user_id>[^/.]+)')
    def user_timeline(self, request, user_id=None):
        """
        Timeline complète d'un utilisateur avec pagination.
        
        Agrège TOUS les logs liés à :
        1. L'utilisateur lui-même (objet User modifié)
        2. Ses demandes (ProspectRequest où source=user)
        3. Ses offres (Offer liées aux demandes)
        4. Ses devis (Quote liés aux offres)
        5. Ses installations (Form liées aux offres)
        6. Ses factures (Invoice liées aux installations)
        7. TOUS les logs où il est l'acteur (peu importe l'objet)
        
        GET /api/admin-platform/audit-logs/user-timeline/{user_id}/?page=1
        
        Retourne une réponse paginée avec count, next, previous, results.
        """
        # Activer la pagination pour cette action uniquement
        self.pagination_class = TimelinePagination
        
        from users.models import User
        from request.models import ProspectRequest
        from offers.models import Offer
        from billing.models import Quote
        from installations.models import Form
        from invoices.models import Invoice
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Content types
        user_ct = ContentType.objects.get_for_model(User)
        request_ct = ContentType.objects.get_for_model(ProspectRequest)
        offer_ct = ContentType.objects.get_for_model(Offer)
        quote_ct = ContentType.objects.get_for_model(Quote)
        form_ct = ContentType.objects.get_for_model(Form)
        invoice_ct = ContentType.objects.get_for_model(Invoice)
        
        # Récupérer tous les objets liés à l'utilisateur
        requests = ProspectRequest.objects.filter(source=user)
        offers = Offer.objects.filter(request__in=requests)
        quotes = Quote.objects.filter(offer__in=offers)
        forms = Form.objects.filter(offer__in=offers)
        invoices = Invoice.objects.filter(installation__in=forms)
        
        # Convertir les IDs en strings (auditlog stocke object_pk en string)
        request_pks = [str(r.pk) for r in requests] if requests.exists() else []
        offer_pks = [str(o.pk) for o in offers] if offers.exists() else []
        quote_pks = [str(q.pk) for q in quotes] if quotes.exists() else []
        form_pks = [str(f.pk) for f in forms] if forms.exists() else []
        invoice_pks = [str(i.pk) for i in invoices] if invoices.exists() else []
        
        # Construire la requête de logs
        # IMPORTANT: Inclure TOUS les logs où user est acteur + objets liés
        query = models.Q(actor_id=user.id)  # Tous les logs où il est acteur
        query |= models.Q(content_type=user_ct, object_pk=str(user.pk))  # User lui-même
        
        if request_pks:
            query |= models.Q(content_type=request_ct, object_pk__in=request_pks)
        if offer_pks:
            query |= models.Q(content_type=offer_ct, object_pk__in=offer_pks)
        if quote_pks:
            query |= models.Q(content_type=quote_ct, object_pk__in=quote_pks)
        if form_pks:
            query |= models.Q(content_type=form_ct, object_pk__in=form_pks)
        if invoice_pks:
            query |= models.Q(content_type=invoice_ct, object_pk__in=invoice_pks)
        
        logs = LogEntry.objects.filter(query).select_related('actor', 'content_type').order_by('-timestamp')
        
        # Appliquer la pagination
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # Ajouter les infos utilisateur à la réponse paginée
            response.data['user'] = {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name(),
            }
            return response
        
        # Fallback sans pagination (ne devrait pas arriver)
        serializer = self.get_serializer(logs, many=True)
        return Response({
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.get_full_name(),
            },
            'logs': serializer.data,
            'count': logs.count(),
        })

