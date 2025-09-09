from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from decimal import Decimal

from .models import Invoice, InvoiceLine, Installment, Payment
from .serializers import InvoiceSerializer, PaymentSerializer, InstallmentSerializer
from authentication.permissions import IsAdmin, HasRequestsAccess


class InvoiceViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Invoice.objects.all().select_related("installation", "quote").prefetch_related("lines", "installments", "payments")
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

        # Si une facture existe déjà, retourner la plus récente
        existing = Invoice.objects.filter(installation=installation).order_by("-created_at").first()
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
    queryset = Installment.objects.all().select_related("invoice")
    serializer_class = InstallmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # list/retrieve/create => HasRequestsAccess; update/partial_update/destroy => IsAdmin
        if self.action in ("list", "retrieve", "create"):
            return [HasRequestsAccess()]
        return [IsAdmin()]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related("invoice", "installment")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # list/retrieve/create => HasRequestsAccess; update/partial_update/destroy => IsAdmin
        if self.action in ("list", "retrieve", "create"):
            return [HasRequestsAccess()]
        return [IsAdmin()]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        # refresh statuses
        invoice = instance.invoice
        # Update installment paid state
        if instance.installment and instance.installment.amount:
            total_paid = instance.installment.payments.aggregate(s=models.Sum("amount")).get("s") or Decimal("0")
            is_paid = total_paid >= (instance.installment.amount or Decimal("0"))
            if instance.installment.is_paid != is_paid:
                instance.installment.is_paid = is_paid
                instance.installment.save(update_fields=["is_paid", "updated_at"])
        invoice.refresh_status()
        invoice.save(update_fields=["status", "updated_at"]) 

    def perform_update(self, serializer):
        instance = serializer.save()
        # refresh statuses
        invoice = instance.invoice
        if instance.installment and instance.installment.amount:
            total_paid = instance.installment.payments.aggregate(s=models.Sum("amount")).get("s") or Decimal("0")
            is_paid = total_paid >= (instance.installment.amount or Decimal("0"))
            if instance.installment.is_paid != is_paid:
                instance.installment.is_paid = is_paid
                instance.installment.save(update_fields=["is_paid", "updated_at"])
        invoice.refresh_status()
        invoice.save(update_fields=["status", "updated_at"]) 

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
