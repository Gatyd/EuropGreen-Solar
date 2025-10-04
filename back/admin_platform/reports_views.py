"""
Vues pour la génération de rapports.
Exports comptables, rapports de ventes, commissions, prospects.
"""

import csv
import io
from datetime import datetime
from decimal import Decimal

from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg, F, Value, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Import des modèles
from invoices.models import Invoice
from billing.models import Quote
from request.models import ProspectRequest
from installations.models import Form
from users.models import User


class ReportsViewSet(viewsets.GenericViewSet):
    """
    ViewSet pour la génération de rapports et exports.
    """
    # DRF nécessite un queryset pour le router, même si on n'utilise que des @action
    queryset = Invoice.objects.none()
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def _get_date_range(self, request):
        """Extrait la période depuis les paramètres de requête."""
        start_str = request.query_params.get('start_date')
        end_str = request.query_params.get('end_date')
        
        if start_str and end_str:
            start_date = timezone.make_aware(datetime.strptime(start_str, '%Y-%m-%d'))
            end_date = timezone.make_aware(datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
        else:
            # Par défaut : 1 an
            end_date = timezone.now()
            start_date = end_date.replace(year=end_date.year - 1)
        
        return start_date, end_date
    
    @extend_schema(
        summary="Export comptable",
        description="Export des factures au format CSV ou Excel pour intégration comptable.",
        parameters=[
            OpenApiParameter(name='start_date', description='Date début (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='end_date', description='Date fin (YYYY-MM-DD)', required=False, type=str),
            OpenApiParameter(name='status', description='Statut factures (all, paid, issued, partially_paid)', required=False, type=str),
            OpenApiParameter(name='export_format', description='Format export (csv, excel)', required=False, type=str),
        ]
    )
    @action(detail=False, methods=['get'], url_path='accounting-export')
    def accounting_export(self, request):
        """
        Export comptable des factures.
        
        Colonnes exportées :
        - Numéro facture
        - Date émission
        - Date échéance
        - Client (nom complet)
        - Montant HT
        - Taux TVA (%)
        - Montant TVA (€)
        - Montant TTC
        - Statut
        - Notes
        """
        start_date, end_date = self._get_date_range(request)
        status_filter = request.query_params.get('status', 'all')
        export_format = request.query_params.get('export_format', 'csv')
        
        # Récupérer les factures
        invoices = Invoice.objects.filter(
            created_at__range=[start_date, end_date]
        ).select_related('installation__client')
        
        # Filtrer par statut si demandé
        if status_filter != 'all':
            if status_filter == 'paid':
                invoices = invoices.filter(status='paid')
            elif status_filter == 'issued':
                invoices = invoices.filter(status='issued')
            elif status_filter == 'partially_paid':
                invoices = invoices.filter(status='partially_paid')
        
        invoices = invoices.order_by('issue_date')
        
        # Préparer les données
        data = []
        for inv in invoices:
            client = inv.installation.client if inv.installation and inv.installation.client else None
            client_name = f"{client.last_name} {client.first_name}" if client else "Client inconnu"
            
            # Calculer TVA
            subtotal = float(inv.subtotal)
            tax_rate = float(inv.tax_rate)
            tax_amount = subtotal * (tax_rate / 100)
            total = float(inv.total)
            
            # Statut en français
            status_labels = {
                'draft': 'Brouillon',
                'issued': 'Émise',
                'partially_paid': 'Partiellement payée',
                'paid': 'Payée',
                'cancelled': 'Annulée'
            }
            
            data.append({
                'number': inv.number or f"INV-{inv.id}",
                'issue_date': inv.issue_date.strftime('%d/%m/%Y') if inv.issue_date else '',
                'due_date': inv.due_date.strftime('%d/%m/%Y') if inv.due_date else '',
                'client': client_name,
                'subtotal': subtotal,
                'tax_rate': tax_rate,
                'tax_amount': tax_amount,
                'total': total,
                'status': status_labels.get(inv.status, inv.status),
                'notes': inv.notes or ''
            })
        
        # Générer l'export selon le format
        if export_format == 'excel' and EXCEL_AVAILABLE:
            return self._generate_excel_export(data, start_date, end_date)
        else:
            return self._generate_csv_export(data, start_date, end_date)
    
    def _generate_csv_export(self, data, start_date, end_date):
        """Génère un export CSV."""
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-têtes
        headers = [
            'Numéro Facture',
            'Date Émission',
            'Date Échéance',
            'Client',
            'Montant HT (€)',
            'TVA (%)',
            'TVA (€)',
            'Montant TTC (€)',
            'Statut',
            'Notes'
        ]
        writer.writerow(headers)
        
        # Données
        for row in data:
            writer.writerow([
                row['number'],
                row['issue_date'],
                row['due_date'],
                row['client'],
                f"{row['subtotal']:.2f}".replace('.', ','),
                f"{row['tax_rate']:.2f}".replace('.', ','),
                f"{row['tax_amount']:.2f}".replace('.', ','),
                f"{row['total']:.2f}".replace('.', ','),
                row['status'],
                row['notes']
            ])
        
        # Ligne de total
        if data:
            total_ht = sum(r['subtotal'] for r in data)
            total_tva = sum(r['tax_amount'] for r in data)
            total_ttc = sum(r['total'] for r in data)
            
            writer.writerow([])
            writer.writerow([
                'TOTAL',
                '',
                '',
                '',
                f"{total_ht:.2f}".replace('.', ','),
                '',
                f"{total_tva:.2f}".replace('.', ','),
                f"{total_ttc:.2f}".replace('.', ','),
                '',
                ''
            ])
        
        # Préparer la réponse
        output.seek(0)
        response = HttpResponse(output.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8-sig')
        filename = f"export_comptable_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _generate_excel_export(self, data, start_date, end_date):
        """Génère un export Excel avec mise en forme."""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Export Comptable"
        
        # Styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # En-têtes
        headers = [
            'Numéro Facture',
            'Date Émission',
            'Date Échéance',
            'Client',
            'Montant HT (€)',
            'TVA (%)',
            'TVA (€)',
            'Montant TTC (€)',
            'Statut',
            'Notes'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
        
        # Données
        for row_num, row_data in enumerate(data, 2):
            ws.cell(row=row_num, column=1, value=row_data['number']).border = border
            ws.cell(row=row_num, column=2, value=row_data['issue_date']).border = border
            ws.cell(row=row_num, column=3, value=row_data['due_date']).border = border
            ws.cell(row=row_num, column=4, value=row_data['client']).border = border
            ws.cell(row=row_num, column=5, value=row_data['subtotal']).border = border
            ws.cell(row=row_num, column=6, value=row_data['tax_rate']).border = border
            ws.cell(row=row_num, column=7, value=row_data['tax_amount']).border = border
            ws.cell(row=row_num, column=8, value=row_data['total']).border = border
            ws.cell(row=row_num, column=9, value=row_data['status']).border = border
            ws.cell(row=row_num, column=10, value=row_data['notes']).border = border
            
            # Format numérique pour les montants
            for col in [5, 6, 7, 8]:
                ws.cell(row=row_num, column=col).number_format = '#,##0.00'
        
        # Ligne de total
        if data:
            total_row = len(data) + 3
            ws.cell(row=total_row, column=1, value='TOTAL').font = Font(bold=True)
            ws.cell(row=total_row, column=5, value=sum(r['subtotal'] for r in data)).font = Font(bold=True)
            ws.cell(row=total_row, column=5).number_format = '#,##0.00'
            ws.cell(row=total_row, column=7, value=sum(r['tax_amount'] for r in data)).font = Font(bold=True)
            ws.cell(row=total_row, column=7).number_format = '#,##0.00'
            ws.cell(row=total_row, column=8, value=sum(r['total'] for r in data)).font = Font(bold=True)
            ws.cell(row=total_row, column=8).number_format = '#,##0.00'
        
        # Ajuster les largeurs de colonnes
        ws.column_dimensions['A'].width = 18
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 15
        ws.column_dimensions['D'].width = 25
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 16
        ws.column_dimensions['I'].width = 18
        ws.column_dimensions['J'].width = 30
        
        # Sauvegarder dans un buffer
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Préparer la réponse
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"export_comptable_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
