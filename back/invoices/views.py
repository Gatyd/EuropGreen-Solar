from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import models, transaction
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.files.base import ContentFile
import asyncio
import re

from .models import Invoice, InvoiceLine, Installment, Payment
from .serializers import InvoiceSerializer, PaymentSerializer, InstallmentSerializer
from authentication.permissions import IsAdmin, HasRequestsAccess, HasAdministrativeAccess


class InvoiceViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Invoice.objects.all().select_related("installation", "quote")
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'installation': ['isnull'],
    }

    def get_permissions(self):
        """Safe methods: IsAuthenticated, sinon HasAdministrativeAccess."""
        if self.action in permissions.SAFE_METHODS or self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [HasAdministrativeAccess()]

    def create(self, request, *args, **kwargs):
        """Créer une facture.

        Deux modes:
        1. Facture normale (process client): { installation: <uuid> }
        2. Facture standalone: { custom_recipient_name: "...", lines: [...], ... } (pas d'installation)
        """
        installation_id = request.data.get("installation")
        
        # Mode standalone: pas d'installation fournie
        if not installation_id:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Créer la facture
            invoice = serializer.save(
                created_by=request.user,
                updated_by=request.user,
                status=Invoice.Status.DRAFT,
            )
            
            # Gérer les lignes si fournies
            lines_data = request.data.get("lines", [])
            if lines_data:
                self._create_invoice_lines(invoice, lines_data)
            
            serializer = self.get_serializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Mode normal: à partir d'une installation
        from installations.models import Form as InstallationForm
        from billing.models import Quote

        installation = get_object_or_404(InstallationForm, pk=installation_id)

        existing = Invoice.objects.filter(installation=installation).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        quote = Quote.objects.filter(offer=installation.offer, status="accepted").order_by("-created_at", "-version").first()
        if not quote:
            return Response({"detail": "Aucun devis accepté trouvé pour cette fiche."}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(
            installation=installation,
            quote=quote,
            title=f"Facture pour devis {quote.number}" if getattr(quote, "number", None) else "Facture",
            currency=getattr(quote, "currency", "EUR"),
            subtotal=quote.subtotal,
            discount_amount=quote.discount_amount,
            tax_rate=quote.tax_rate,
            total=quote.total,
            created_by=request.user if request.user and request.user.is_authenticated else None,
            updated_by=request.user if request.user and request.user.is_authenticated else None,
            status=Invoice.Status.ISSUED,
        )

        # Copier les lignes du devis
        quote_lines = quote.lines.all().order_by("position", "created_at")
        bulk_lines = []
        for ql in quote_lines:
            bulk_lines.append(InvoiceLine(
                invoice=invoice,
                product_type=ql.product_type,
                name=ql.name,
                description=ql.description,
                unit_price=ql.unit_price,
                cost_price=ql.cost_price,
                quantity=ql.quantity,
                discount_rate=ql.discount_rate,
                line_total=ql.line_total,
                position=ql.position,
            ))
        if bulk_lines:
            InvoiceLine.objects.bulk_create(bulk_lines)

        serializer = self.get_serializer(invoice)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Mettre à jour une facture (standalone uniquement)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if not instance.is_standalone:
            return Response(
                {"detail": "Seules les factures standalone peuvent être modifiées."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if instance.status not in (Invoice.Status.DRAFT, Invoice.Status.ISSUED):
            return Response(
                {"detail": "Impossible de modifier une facture payée ou annulée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Gérer les lignes séparément si fournies
        lines_data = request.data.pop("lines", None)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Mettre à jour les lignes si fournies
        if lines_data is not None:
            self._update_invoice_lines(instance, lines_data)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def _create_invoice_lines(self, invoice: Invoice, lines_data: list) -> None:
        """Créer les lignes de facture et recalculer les totaux."""
        with transaction.atomic():
            subtotal = Decimal("0")
            bulk_lines = []
            
            for idx, line_data in enumerate(lines_data):
                unit_price = Decimal(str(line_data.get("unit_price", 0)))
                quantity = Decimal(str(line_data.get("quantity", 1)))
                discount_rate = Decimal(str(line_data.get("discount_rate", 0)))
                
                line_subtotal = unit_price * quantity
                discount_amount = line_subtotal * (discount_rate / 100)
                line_total = line_subtotal - discount_amount
                
                bulk_lines.append(InvoiceLine(
                    invoice=invoice,
                    product_type=line_data.get("product_type", "other"),
                    name=line_data.get("name", ""),
                    description=line_data.get("description", ""),
                    unit_price=unit_price,
                    cost_price=Decimal(str(line_data.get("cost_price", 0))),
                    quantity=quantity,
                    discount_rate=discount_rate,
                    line_total=line_total,
                    position=idx,
                ))
                subtotal += line_total
            
            if bulk_lines:
                InvoiceLine.objects.bulk_create(bulk_lines)
            
            # Mettre à jour totaux
            invoice.subtotal = subtotal
            tax_amount = subtotal * (invoice.tax_rate / 100)
            invoice.total = subtotal + tax_amount
            invoice.save(update_fields=["subtotal", "total", "updated_at"])

    def _update_invoice_lines(self, invoice: Invoice, lines_data: list) -> None:
        """Remplacer toutes les lignes de facture et recalculer les totaux."""
        with transaction.atomic():
            # Supprimer anciennes lignes
            invoice.lines.all().delete()
            
            # Créer nouvelles lignes
            self._create_invoice_lines(invoice, lines_data)


class InstallmentViewSet(viewsets.ModelViewSet):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["invoice"]

    def get_permissions(self):
        # list/retrieve/create => HasRequestsAccess; update/partial_update/destroy => IsAdmin
        if self.action in ("list", "retrieve", "create"):
            return [HasRequestsAccess()]
        return [IsAdmin()]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["invoice"]

    def get_permissions(self):
        # list/retrieve/create => HasRequestsAccess; update/partial_update/destroy => IsAdmin
        if self.action in ("list", "retrieve", "create"):
            return [HasRequestsAccess()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        invoice = self._post_payment_common(instance)
        self._maybe_generate_invoice_pdf(invoice)

    def perform_update(self, serializer):
        instance = serializer.save()
        invoice = self._post_payment_common(instance)
        self._maybe_generate_invoice_pdf(invoice)

    def perform_destroy(self, instance):
        invoice = instance.invoice
        installment = instance.installment
        super().perform_destroy(instance)
        # Recompute after delete
        if installment and installment.amount:
            total_paid = installment.payments.aggregate(s=models.Sum("amount")).get("s") or Decimal("0")
            is_paid = total_paid >= (installment.amount or Decimal("0"))
            if installment.is_paid != is_paid:
                installment.is_paid = is_paid
                installment.save(update_fields=["is_paid", "updated_at"])
        invoice.refresh_status()
        invoice.save(update_fields=["status", "updated_at"]) 

    # ------------------------- Utilitaires internes ------------------------- #
    def _post_payment_common(self, payment: Payment) -> Invoice:
        """Met à jour l'échéance liée et le statut de la facture après un paiement."""
        invoice = payment.invoice
        if payment.installment and payment.installment.amount:
            total_paid = payment.installment.payments.aggregate(s=models.Sum("amount")).get("s") or Decimal("0")
            is_paid = total_paid >= (payment.installment.amount or Decimal("0"))
            if payment.installment.is_paid != is_paid:
                payment.installment.is_paid = is_paid
                payment.installment.save(update_fields=["is_paid", "updated_at"])
        invoice.refresh_status()
        invoice.save(update_fields=["status", "updated_at"])
        return invoice

    def _maybe_generate_invoice_pdf(self, invoice: Invoice) -> None:
        """Génère et enregistre le PDF de facture si totalement payée et pas déjà généré.

        Conditions:
        - total > 0
        - amount_paid >= total
        - pas de pdf existant (on évite la régénération pour l'instant)
        """
        try:
            if not invoice.total or invoice.total <= 0:
                return
            if invoice.amount_paid < invoice.total:
                return
            if invoice.pdf:  # déjà généré
                return
            pdf_bytes = self._render_invoice_pdf(invoice)
            if not pdf_bytes:
                return
            safe_number = re.sub(r"[^A-Za-z0-9_-]", "_", invoice.number or str(invoice.id))
            filename = f"{safe_number}.pdf"
            invoice.pdf.save(filename, ContentFile(pdf_bytes), save=False)
            invoice.refresh_status()  # statut peut dépendre de la présence du PDF
            invoice.save(update_fields=["pdf", "status", "updated_at"])
        except Exception:
            # On ignore silencieusement pour ne pas bloquer l'API paiement
            pass

    # --------------------- Génération PDF via Playwright --------------------- #
    def _render_invoice_pdf(self, invoice: Invoice) -> bytes | None:
        """Rend le PDF de la facture via la page front dédiée.

        Retourne les bytes du PDF ou None si échec.
        """
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        
        # Adapter l'URL selon le type de facture
        if invoice.is_standalone:
            url = f"{base_url}/print/standalone-invoice/{invoice.id}"
        else:
            if not invoice.installation_id:
                return None
            form_id = str(invoice.installation_id)
            url = f"{base_url}/print/installation-form/{form_id}/invoice"

        async def _async_render() -> bytes:
            from playwright.async_api import async_playwright  # type: ignore
            async with async_playwright() as p:
                browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])  # type: ignore
                context = await browser.new_context()
                try:
                    page = await context.new_page()
                    await page.goto(url, wait_until="networkidle")
                    pdf_bytes = await page.pdf(
                        format="A4",
                        print_background=True,
                        display_header_footer=True,
                        footer_template='''
                            <div style="font-size:10px; color:#666; width:100%; padding:6px 10px; text-align:center;">
                                Page <span class="pageNumber"></span> / <span class="totalPages"></span>
                            </div>
                        ''',
                    )
                    return pdf_bytes
                finally:
                    try:
                        await context.close()
                    except Exception:
                        pass
                    try:
                        await browser.close()
                    except Exception:
                        pass

        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop and loop.is_running():
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(_async_render())
                finally:
                    new_loop.close()
            else:
                return asyncio.run(_async_render())
        except Exception:
            return None
