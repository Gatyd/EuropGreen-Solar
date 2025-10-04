"""
Vues pour le tableau de bord administrateur.
Fournit des statistiques et KPIs sur l'activité de l'entreprise.
"""

from django.db.models import Count, Sum, F, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from datetime import timedelta, datetime
from decimal import Decimal

# Import des modèles
from request.models import ProspectRequest
from offers.models import Offer
from billing.models import Quote, QuoteLine
from installations.models import Form
from invoices.models import Invoice


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour le tableau de bord administrateur.
    Fournit des statistiques et indicateurs de performance.
    """
    
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def _validate_date_string(self, date_str):
        """
        Valide une chaîne de date pour éviter les dates absurdes comme '12121-01-01'.
        
        Retourne la date si valide, None sinon.
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Vérifier que l'année est raisonnable (entre 1900 et 2100)
            if date_obj.year < 1900 or date_obj.year > 2100:
                return None
            # Vérifier que la date n'est pas dans le futur
            if date_obj > datetime.now():
                return None
            return date_obj
        except (ValueError, TypeError):
            return None
    
    def _get_date_range(self, request):
        """
        Extrait la période demandée depuis les paramètres de requête.
        
        Paramètres:
        - period: '7d', '30d', '6m', '1y', 'custom'
        - start_date: date de début (format YYYY-MM-DD) si period='custom'
        - end_date: date de fin (format YYYY-MM-DD) si period='custom'
        
        Retourne: (start_date, end_date)
        """
        period = request.query_params.get('period', '30d')
        end_date = timezone.now()
        
        if period == 'custom':
            start_str = request.query_params.get('start_date')
            end_str = request.query_params.get('end_date')
            if start_str and end_str:
                # Valider les dates avant de les parser
                start_parsed = self._validate_date_string(start_str)
                end_parsed = self._validate_date_string(end_str)
                
                if start_parsed and end_parsed:
                    start_date = timezone.make_aware(start_parsed)
                    end_date = timezone.make_aware(end_parsed)
                else:
                    # Fallback sur 1 an par défaut si validation échoue
                    start_date = end_date - timedelta(days=365)
            else:
                # Fallback sur 30 jours par défaut
                start_date = end_date - timedelta(days=30)
        elif period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    @extend_schema(
        summary="Vue d'ensemble - KPIs principaux",
        description="Retourne les 4 indicateurs clés : projets actifs, CA, taux de conversion, commissions à verser.",
        parameters=[
            OpenApiParameter(name='period', description='Période (7d, 30d, 6m, 1y, custom)', required=False, type=str),
            OpenApiParameter(name='start_date', description='Date début (YYYY-MM-DD) si period=custom', required=False, type=str),
            OpenApiParameter(name='end_date', description='Date fin (YYYY-MM-DD) si period=custom', required=False, type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        KPIs principaux pour les cards du dashboard.
        
        Retourne:
        {
            "active_projects": 42,
            "revenue": {
                "total": 150000.00,
                "pending": 25000.00,
                "potential": 80000.00
            },
            "conversion_rate": 35.5,
            "commissions_due": 12500.00
        }
        """
        start_date, end_date = self._get_date_range(request)
        
        # 1. Projets actifs (demandes + offres + installations en cours)
        active_requests = ProspectRequest.objects.filter(
            status__in=['new', 'followup', 'in_progress']
        ).count()
        
        active_offers = Offer.objects.exclude(
            status='quote_signed'
        ).exclude(
            installation_moved_at__isnull=False
        ).count()
        
        active_installations = Form.objects.exclude(
            status='commissioning'
        ).count()
        
        active_projects = active_requests + active_offers + active_installations
        
        # 2. Chiffre d'affaires
        # CA total (factures payées)
        revenue_total = Invoice.objects.filter(
            status='paid',
            created_at__range=[start_date, end_date]
        ).aggregate(total=Coalesce(Sum('total'), Decimal('0')))['total']
        
        # CA en attente (factures émises non payées)
        revenue_pending = Invoice.objects.filter(
            status__in=['issued', 'partially_paid'],
            created_at__range=[start_date, end_date]
        ).aggregate(total=Coalesce(Sum('total'), Decimal('0')))['total']
        
        # CA potentiel (devis envoyés/en négociation non signés)
        revenue_potential = Quote.objects.filter(
            status__in=['sent', 'pending'],
            created_at__range=[start_date, end_date]
        ).aggregate(total=Coalesce(Sum('total'), Decimal('0')))['total']
        
        # 3. Taux de conversion global (demandes → installations terminées)
        total_requests = ProspectRequest.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        completed_installations = Form.objects.filter(
            status='commissioning',
            created_at__range=[start_date, end_date]
        ).count()
        
        conversion_rate = (completed_installations / total_requests * 100) if total_requests > 0 else 0
        
        # 4. Commissions à verser (non payées)
        commissions_collaborator = Form.objects.filter(
            commission_paid=False,
            commission_amount__gt=0
        ).aggregate(total=Coalesce(Sum('commission_amount'), Decimal('0')))['total']
        
        commissions_sales = Form.objects.filter(
            sales_commission_paid=False,
            sales_commission_amount__gt=0
        ).aggregate(total=Coalesce(Sum('sales_commission_amount'), Decimal('0')))['total']
        
        commissions_due = commissions_collaborator + commissions_sales
        
        return Response({
            'active_projects': active_projects,
            'revenue': {
                'total': float(revenue_total),
                'pending': float(revenue_pending),
                'potential': float(revenue_potential)
            },
            'conversion_rate': round(conversion_rate, 2),
            'commissions_due': float(commissions_due)
        })
    
    @extend_schema(
        summary="Funnel de conversion",
        description="Données pour le graphique en entonnoir : Demandes → Offres → Devis signés → Installations.",
        parameters=[
            OpenApiParameter(name='period', description='Période', required=False, type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def conversion_funnel(self, request):
        """
        Données pour le funnel de conversion.
        
        Retourne:
        {
            "stages": [
                {"name": "Demandes reçues", "count": 100, "percentage": 100},
                {"name": "Offres créées", "count": 75, "percentage": 75},
                {"name": "Devis signés", "count": 45, "percentage": 45},
                {"name": "Installations terminées", "count": 38, "percentage": 38}
            ]
        }
        """
        start_date, end_date = self._get_date_range(request)
        
        # Compter chaque étape
        requests_count = ProspectRequest.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        offers_count = Offer.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        signed_quotes_count = Quote.objects.filter(
            status='accepted',
            created_at__range=[start_date, end_date]
        ).count()
        
        completed_installations = Form.objects.filter(
            status='commissioning',
            created_at__range=[start_date, end_date]
        ).count()
        
        # Calculer les pourcentages (base = demandes)
        base = requests_count if requests_count > 0 else 1
        
        stages = [
            {
                'name': 'Demandes reçues',
                'count': requests_count,
                'percentage': 100
            },
            {
                'name': 'Offres créées',
                'count': offers_count,
                'percentage': round((offers_count / base) * 100, 2)
            },
            {
                'name': 'Devis signés',
                'count': signed_quotes_count,
                'percentage': round((signed_quotes_count / base) * 100, 2)
            },
            {
                'name': 'Installations terminées',
                'count': completed_installations,
                'percentage': round((completed_installations / base) * 100, 2)
            }
        ]
        
        return Response({'stages': stages})
    
    @extend_schema(
        summary="Évolution du chiffre d'affaires",
        description="Données temporelles pour le graphique d'évolution du CA.",
        parameters=[
            OpenApiParameter(name='period', description='Période', required=False, type=str),
        ]
    )
    @action(detail=False, methods=['get'])
    def revenue_chart(self, request):
        """
        Évolution du CA sur la période sélectionnée.
        
        Retourne:
        {
            "labels": ["Jan 2025", "Fév 2025", ...],
            "data": [15000, 22000, 18500, ...]
        }
        """
        start_date, end_date = self._get_date_range(request)
        
        # Grouper par mois (utiliser created_at pour cohérence avec overview)
        revenue_by_month = Invoice.objects.filter(
            status='paid',
            created_at__range=[start_date, end_date]
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Coalesce(Sum('total'), Decimal('0'))
        ).order_by('month')
        
        # Créer un dictionnaire des revenus par mois (datetime -> float)
        revenue_dict = {
            item['month']: float(item['total'])
            for item in revenue_by_month
        }
        
        # Générer tous les mois de la période
        labels = []
        data = []
        current = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        while current <= end_date:
            # Chercher la valeur en comparant année et mois seulement
            month_value = 0
            for db_month, total in revenue_dict.items():
                if db_month.year == current.year and db_month.month == current.month:
                    month_value = total
                    break
            
            labels.append(current.strftime('%b %Y'))
            data.append(month_value)
            
            # Passer au mois suivant
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return Response({
            'labels': labels,
            'data': data
        })
    
    @extend_schema(
        summary="Répartition des sources de prospects",
        description="Distribution des demandes par source pour graphique pie chart.",
    )
    @action(detail=False, methods=['get'])
    def sources_breakdown(self, request):
        """
        Répartition des demandes par source.
        
        Retourne:
        {
            "labels": ["Call Center", "Formulaire Web", ...],
            "data": [45, 30, 15, 8, 2],
            "conversion_rates": [35.5, 42.1, ...]
        }
        """
        start_date, end_date = self._get_date_range(request)
        
        sources = ProspectRequest.objects.filter(
            created_at__range=[start_date, end_date]
        ).values('source_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Calculer taux de conversion par source
        labels = []
        data = []
        conversion_rates = []
        
        source_labels = {
            'call_center': 'Call Center',
            'web_form': 'Formulaire Web',
            'client': 'Client',
            'collaborator': 'Collaborateur',
            'commercial': 'Commercial'
        }
        
        for source in sources:
            source_type = source['source_type']
            count = source['count']
            
            # Calculer taux de conversion pour cette source
            converted = ProspectRequest.objects.filter(
                source_type=source_type,
                created_at__range=[start_date, end_date],
                converted_decision=True
            ).count()
            
            conversion_rate = (converted / count * 100) if count > 0 else 0
            
            labels.append(source_labels.get(source_type, source_type))
            data.append(count)
            conversion_rates.append(round(conversion_rate, 2))
        
        return Response({
            'labels': labels,
            'data': data,
            'conversion_rates': conversion_rates
        })
    
    @extend_schema(
        summary="Performance des produits",
        description="Statistiques de vente par type de produit.",
    )
    @action(detail=False, methods=['get'])
    def products_performance(self, request):
        """
        Performance des produits vendus.
        
        Retourne:
        {
            "labels": ["Panneaux", "Onduleurs", ...],
            "quantities": [245, 189, ...],
            "revenue": [125000, 98000, ...]
        }
        """
        start_date, end_date = self._get_date_range(request)
        
        # Récupérer les lignes de devis signés
        product_stats = QuoteLine.objects.filter(
            quote__status='accepted',
            quote__created_at__range=[start_date, end_date]
        ).values('product_type').annotate(
            total_quantity=Coalesce(Sum('quantity'), Decimal('0'), output_field=DecimalField()),
            total_revenue=Coalesce(
                Sum(F('quantity') * F('unit_price'), output_field=DecimalField()), 
                Decimal('0'),
                output_field=DecimalField()
            )
        ).order_by('-total_revenue')
        
        type_labels = {
            'panel': 'Panneaux',
            'inverter': 'Onduleurs',
            'battery': 'Batteries',
            'structure': 'Structures',
            'service': 'Services',
            'other': 'Autres'
        }
        
        labels = []
        quantities = []
        revenue = []
        
        for stat in product_stats:
            product_type = stat['product_type']
            labels.append(type_labels.get(product_type, product_type))
            quantities.append(stat['total_quantity'])
            revenue.append(float(stat['total_revenue']))
        
        return Response({
            'labels': labels,
            'quantities': quantities,
            'revenue': revenue
        })
