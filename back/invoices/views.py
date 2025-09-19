from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.files.base import ContentFile
import asyncio
import re

from .models import Invoice, InvoiceLine, Installment, Payment
from .serializers import InvoiceSerializer, PaymentSerializer, InstallmentSerializer
from authentication.permissions import IsAdmin, HasRequestsAccess


class InvoiceViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    # Réponses plus légères; les échéances/paiements seront récupérés via endpoints dédiés filtrés par facture
    queryset = Invoice.objects.all().select_related("installation", "quote")
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """Créer une facture à partir de la fiche d'installation.

        - Body attendu: { installation: <uuid> }
        - Si une facture existe déjà pour cette fiche, la retourner.
        - Sinon, trouver le dernier devis ACCEPTÉ de l'offre liée à la fiche et copier ses lignes/totaux.
        """
        installation_id = request.data.get("installation")
        if not installation_id:
            return Response({"detail": "Paramètre 'installation' requis."}, status=status.HTTP_400_BAD_REQUEST)

        from installations.models import Form as InstallationForm
        from billing.models import Quote

        installation = get_object_or_404(InstallationForm, pk=installation_id)

        existing = Invoice.objects.filter(installation=installation).first()
        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Dernier devis accepté de l'offre liée à la fiche
        quote = Quote.objects.filter(offer=installation.offer, status="accepted").order_by("-created_at", "-version").first()
        if not quote:
            return Response({"detail": "Aucun devis accepté trouvé pour cette fiche."}, status=status.HTTP_400_BAD_REQUEST)

        # Créer la facture en copiant les totaux principaux
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
            status=Invoice.Status.ISSUED,  # émise directement (peut être ajusté plus tard)
        )

        # Copier les lignes
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
        form_id = str(invoice.installation_id)
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
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
