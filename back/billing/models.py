from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class Product(models.Model):
	class Type(models.TextChoices):
		PANEL = "panel", "Panneau"
		INVERTER = "inverter", "Onduleur"
		BATTERY = "battery", "Batterie"
		STRUCTURE = "structure", "Structure"
		SERVICE = "service", "Service"
		OTHER = "other", "Autre"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	# sku = models.CharField(max_length=64, unique=True)
	name = models.CharField(max_length=255)
	type = models.CharField(max_length=20, choices=Type.choices)
	description = models.TextField(blank=True)
	# unit = models.CharField(max_length=32, default="unité")
	unit_price = models.DecimalField(max_digits=12, decimal_places=2)
	cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "billing_product"
		ordering = ["name"]
		verbose_name = "Produit/Service"
		verbose_name_plural = "Produits/Services"

	def __str__(self) -> str:
		return f"{self.name} ({self.get_type_display()})"


class Quote(models.Model):

	class Status(models.TextChoices):
		DRAFT = "draft", "Brouillon"
		SENT = "sent", "Envoyé"
		ACCEPTED = "accepted", "Accepté"
		DECLINED = "declined", "Refusé"
		PENDING = "pending", "En attente"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	number = models.CharField(max_length=32, unique=True, blank=True)
	offer = models.ForeignKey("offers.Offer", on_delete=models.CASCADE, related_name="quotes")
	# Versionnage
	version = models.PositiveIntegerField(default=1)
	predecessor = models.ForeignKey(
		"self", on_delete=models.SET_NULL, null=True, blank=True, related_name="next_versions"
	)

	status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
	title = models.CharField(max_length=255, blank=True)
	negociations = models.TextField(blank=True)
	notes = models.TextField(blank=True)
	currency = models.CharField(max_length=3, default="EUR")

	valid_until = models.DateField(null=True, blank=True)

	# Totaux simples (HT pour commencer)
	subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20)  # en %
	total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Montant de commission du collaborateur/client (source)")
	sales_commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Montant de commission du commercial (assigned_to)")
	pdf = models.FileField(upload_to="quotes/pdfs/", null=True, blank=True)

	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_quotes"
	)
	updated_by = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_quotes"
	)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "billing_quote"
		ordering = ["-created_at", "-version"]
		verbose_name = "Devis"
		verbose_name_plural = "Devis"
		constraints = [
			models.UniqueConstraint(fields=["offer", "version"], name="uq_quote_offer_version"),
		]

	def __str__(self) -> str:
		return f"Devis {self.number} - {self.get_status_display()}"

	@property
	def is_latest(self) -> bool:
		latest = Quote.objects.filter(offer=self.offer).order_by("-version").values_list("version", flat=True).first()
		return latest == self.version if latest is not None else True

	def clean(self):
		# S'assurer que le prédécesseur appartient à la même offre
		if self.predecessor and self.predecessor.offer_id != self.offer_id:
			from django.core.exceptions import ValidationError

			raise ValidationError({"predecessor": "Le devis précédent doit appartenir à la même offre."})

	def save(self, *args, **kwargs):
		# Auto-incrément de version si un prédécesseur est défini
		if self.predecessor and (self.version is None or self.version <= self.predecessor.version):
			self.version = self.predecessor.version + 1
		elif self.pk is None and (self.version is None or self.version == 0):
			# Si premier enregistrement: choisir max+1 pour l'offre
			last_version = (
				Quote.objects.filter(offer=self.offer).order_by("-version").values_list("version", flat=True).first()
			)
			self.version = (last_version or 0) + 1
		# Générer un numéro unique si manquant: D-YYYY-####
		if not self.number:
			year = timezone.now().year
			base = f"D-{year}-"
			seq = 1
			while True:
				candidate = f"{base}{seq:04d}"
				if not Quote.objects.filter(number=candidate).exists():
					self.number = candidate
					break
				seq += 1
		super().save(*args, **kwargs)


class QuoteLine(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")
	# Pour traçabilité, facultatif
	source_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="used_in_lines")

	# Snapshot des données du produit/service au moment de l'ajout
	product_type = models.CharField(max_length=20, choices=Product.Type.choices)
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	# unit = models.CharField(max_length=32, default="unité")
	unit_price = models.DecimalField(max_digits=12, decimal_places=2)
	cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
	discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # en %
	line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

	position = models.PositiveIntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "billing_quote_line"
		ordering = ["position", "created_at"]
		verbose_name = "Ligne de devis"
		verbose_name_plural = "Lignes de devis"

	def __str__(self) -> str:
		return f"Ligne: {self.name} x{self.quantity}"

	def save(self, *args, **kwargs):
		# Calcul simple du total de ligne
		if self.unit_price is not None and self.quantity is not None:
			price = (self.unit_price or Decimal("0")) * (self.quantity or Decimal("0"))
			discount = (self.discount_rate or Decimal("0")) / Decimal("100")
			factor = Decimal("1") - discount
			self.line_total = (price * factor).quantize(Decimal("0.01"))
		super().save(*args, **kwargs)


class QuoteSignature(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	quote = models.OneToOneField(Quote, on_delete=models.CASCADE, related_name="signature")

	# Données SES (Signature Électronique Simple)
	signer_name = models.CharField(max_length=255, blank=True)
	ip_address = models.GenericIPAddressField(null=True, blank=True)
	user_agent = models.TextField(blank=True)
	signed_at = models.DateTimeField(auto_now_add=True)

	# Capture de la signature
	signature_image = models.ImageField(upload_to="quotes/signatures/", null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "billing_quote_signature"
		verbose_name = "Signature de devis"
		verbose_name_plural = "Signatures de devis"

	def __str__(self) -> str:
		signer = self.signer_name or "Inconnu"
		return f"Signature de {signer} pour devis {self.quote.number}"

