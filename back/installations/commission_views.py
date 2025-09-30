"""
Vues dédiées à la gestion des commissions d'installation.
Modularisation pour améliorer la maintenabilité du code.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Form


class CommissionViewSet(viewsets.ViewSet):
    """
    ViewSet pour la gestion des commissions d'installation.
    Accessible uniquement aux superadmin.
    """
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], url_path='list')
    def list_commissions(self, request):
        """
        Récupère toutes les installations avec des commissions non nulles/non-zero.
        Inclut les informations du client, de la source (collaborateur/client) et du commercial.
        """
        # Filtrer les installations avec au moins une commission non nulle et non zero
        installations = (
            Form.objects
            .select_related('client', 'offer__request__source', 'offer__request__assigned_to')
            .filter(
                Q(commission_amount__gt=0) | Q(sales_commission_amount__gt=0)
            )
            .order_by('-created_at')
        )
        
        results = []
        for installation in installations:
            # Informations client
            client_data = None
            if installation.client:
                client_data = {
                    'id': str(installation.client.id),
                    'first_name': installation.client.first_name,
                    'last_name': installation.client.last_name,
                    'email': installation.client.email,
                }
            
            # Informations demande
            request_data = None
            source_data = None
            assigned_to_data = None
            
            if hasattr(installation, 'offer') and installation.offer:
                offer = installation.offer
                if hasattr(offer, 'request') and offer.request:
                    prospect_request = offer.request
                    request_data = {
                        'id': str(prospect_request.id),
                        'source_type': prospect_request.source_type,
                    }
                    
                    # Source (collaborateur/client apporteur)
                    if prospect_request.source:
                        source_data = {
                            'id': str(prospect_request.source.id),
                            'first_name': prospect_request.source.first_name,
                            'last_name': prospect_request.source.last_name,
                            'email': prospect_request.source.email,
                            'role': prospect_request.source.role,
                        }
                    
                    # Commercial (assigned_to)
                    if prospect_request.assigned_to:
                        assigned_to_data = {
                            'id': str(prospect_request.assigned_to.id),
                            'first_name': prospect_request.assigned_to.first_name,
                            'last_name': prospect_request.assigned_to.last_name,
                            'email': prospect_request.assigned_to.email,
                            'role': prospect_request.assigned_to.role,
                        }
            
            # Construction de la réponse
            results.append({
                'id': str(installation.id),
                'client': client_data,
                'request': request_data,
                'source': source_data,
                'assigned_to': assigned_to_data,
                'commission_amount': float(installation.commission_amount) if installation.commission_amount else 0,
                'commission_paid': installation.commission_paid,
                'sales_commission_amount': float(installation.sales_commission_amount) if installation.sales_commission_amount else 0,
                'sales_commission_paid': installation.sales_commission_paid,
                'created_at': installation.created_at,
            })
        
        return Response(results, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], url_path='pay-source-commission')
    def pay_source_commission(self, request, pk=None):
        """
        Marque la commission du collaborateur/client (source) comme payée.
        """
        try:
            installation = Form.objects.get(pk=pk)
        except Form.DoesNotExist:
            return Response(
                {'error': 'Installation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier qu'il y a bien une commission à payer
        if not installation.commission_amount or installation.commission_amount <= 0:
            return Response(
                {'error': 'Aucune commission source à payer pour cette installation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que la commission n'est pas déjà payée
        if installation.commission_paid:
            return Response(
                {'error': 'La commission source est déjà marquée comme payée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marquer comme payée
        installation.commission_paid = True
        installation.save(update_fields=['commission_paid', 'updated_at'])
        
        return Response(
            {
                'message': 'Commission source marquée comme payée',
                'installation_id': str(installation.id),
                'commission_amount': float(installation.commission_amount),
                'commission_paid': installation.commission_paid,
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['patch'], url_path='pay-sales-commission')
    def pay_sales_commission(self, request, pk=None):
        """
        Marque la commission du commercial (assigned_to) comme payée.
        """
        try:
            installation = Form.objects.get(pk=pk)
        except Form.DoesNotExist:
            return Response(
                {'error': 'Installation non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier qu'il y a bien une commission à payer
        if not installation.sales_commission_amount or installation.sales_commission_amount <= 0:
            return Response(
                {'error': 'Aucune commission commercial à payer pour cette installation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que la commission n'est pas déjà payée
        if installation.sales_commission_paid:
            return Response(
                {'error': 'La commission commercial est déjà marquée comme payée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marquer comme payée
        installation.sales_commission_paid = True
        installation.save(update_fields=['sales_commission_paid', 'updated_at'])
        
        return Response(
            {
                'message': 'Commission commercial marquée comme payée',
                'installation_id': str(installation.id),
                'sales_commission_amount': float(installation.sales_commission_amount),
                'sales_commission_paid': installation.sales_commission_paid,
            },
            status=status.HTTP_200_OK
        )
