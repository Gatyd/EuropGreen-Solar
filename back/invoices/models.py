from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from decimal import Decimal


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        ISSUED = "issued", "Émise"
        PARTIALLY_PAID = "partially_paid", "Partiellement payée"
        PAID = "paid", "Payée"
        CANCELLED = "cancelled", "Annulée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=32, unique=True, blank=True)

    # Lier la facture à la fiche d'installation (pas à l'offre)
    installation = models.OneToOneField(
        "installations.Form", on_delete=models.CASCADE, related_name="invoice"
    )

    # Optionnel: référence au devis accepté qui l'a générée
    quote = models.OneToOneField(
        "billing.Quote", on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_invoice"
    )

    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="EUR")

    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(null=True, blank=True)

    # Totaux (HT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # PDF généré de la facture
    pdf = models.FileField(upload_to="invoices/pdfs/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_invoices"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_invoices"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices_invoice"
        ordering = ["-issue_date", "-created_at"]
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        constraints = [
            models.UniqueConstraint(fields=["installation", "number"], name="uq_invoice_installation_number"),
        ]

    def __str__(self) -> str:
        client_name = self.installation.client.get_full_name() if self.installation.client else "Client inconnu"
        return f"Facture {self.number} - {client_name}"

    @property
    def amount_paid(self) -> Decimal:
        total = self.payments.aggregate(s=models.Sum("amount")) or {"s": Decimal("0")}
        return total.get("s") or Decimal("0")

    @property
    def balance_due(self) -> Decimal:
        return (self.total or Decimal("0")) - self.amount_paid

    def refresh_status(self):
        paid = self.amount_paid
        if self.status == self.Status.CANCELLED:
            return
        if paid <= 0:
            self.status = self.Status.ISSUED if self.pdf else self.Status.DRAFT
        elif paid < self.total:
            self.status = self.Status.PARTIALLY_PAID
        else:
            self.status = self.Status.PAID

    def save(self, *args, **kwargs):
        # Générer un numéro unique si manquant: F-YYYY-####
        if not self.number:
            year = timezone.now().year
            base = f"F-{year}-"
            seq = 1
            while True:
                candidate = f"{base}{seq:04d}"
                if not Invoice.objects.filter(number=candidate).exists():
                    self.number = candidate
                    break
                seq += 1
        super().save(*args, **kwargs)


class InvoiceLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")

    # Copie/snapshot des données de la ligne du devis (pas de FK aux produits pour éviter dilution)
    product_type = models.CharField(max_length=20, choices=(
        ("panel", "Panneau"),
        ("inverter", "Onduleur"),
        ("battery", "Batterie"),
        ("structure", "Structure"),
        ("service", "Service"),
        ("other", "Autre"),
    ))
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    position = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices_invoice_line"
        ordering = ["position", "created_at"]
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"

    def __str__(self) -> str:
        return f"Ligne: {self.name} x{self.quantity}"


class Installment(models.Model):
    """Échéance planifiée (acompte ou échéancier)."""

    class Type(models.TextChoices):
        DEPOSIT = "deposit", "Acompte"
        BALANCE = "balance", "Solde"
        MILESTONE = "milestone", "Échéance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="installments")
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.MILESTONE)
    label = models.CharField(max_length=255, blank=True)
    due_date = models.DateField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    # position supprimé : l'ordre se base maintenant sur due_date puis created_at

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices_installment"
        ordering = ["due_date", "created_at"]
        verbose_name = "Échéance"
        verbose_name_plural = "Échéances"

    def __str__(self) -> str:
        label = self.label or self.get_type_display()
        status = "Payée" if self.is_paid else "En attente"
        return f"Échéance: {label} - {status}"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    installment = models.ForeignKey(Installment, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")

    date = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=50, blank=True)  # virement, CB, chèque, espèces, autre
    reference = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_payments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invoices_payment"
        ordering = ["-date", "-created_at"]
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self) -> str:
        return f"Paiement de {self.amount}€ - {self.date.strftime('%d/%m/%Y')} ({self.method or 'Non précisé'})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour le statut de la facture et l'état de l'échéance liée
        invoice = self.invoice
        if self.installment and self.installment.amount:
            total_paid = self.installment.payments.aggregate(s=models.Sum("amount")).get("s") or Decimal("0")
            if total_paid >= (self.installment.amount or Decimal("0")):
                self.installment.is_paid = True
                self.installment.save(update_fields=["is_paid", "updated_at"])
        invoice.refresh_status()
        invoice.save(update_fields=["status", "updated_at"])
