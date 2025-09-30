from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Signature(models.Model):
    """Signature électronique simple (SES) réutilisable pour les étapes nécessitant une signature).

    Inspiré de billing.QuoteSignature, mais local à l'app `installations` pour éviter les dépendances croisées.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Données SES
    signer_name = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    # Image de signature
    signature_image = models.ImageField(upload_to="installations/signatures/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "installations_signature"
        verbose_name = "Signature"
        verbose_name_plural = "Signatures"

    def __str__(self) -> str:
        return f"Signature {self.id}"

class Form(models.Model):
    class Status(models.TextChoices):
        TECHNICAL_VISIT = "technical_visit", "Visite technique"
        REPRESENTATION_MANDATE = "representation_mandate", "Mandat représentation"
        ADMINISTRATIVE_VALIDATION = "administrative_validation", "Validation administrative"
        INSTALLATION_COMPLETED = "installation_completed", "Installation effectuée"
        CONSUEL_VISIT = "consuel_visit", "Visite CONSUEL"
        ENEDIS_CONNECTION = "enedis_connection", "Raccordement ENEDIS"
        COMMISSIONING = "commissioning", "Mise en service"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer = models.OneToOneField("offers.Offer", on_delete=models.CASCADE, related_name="installations_form")
    # client_first_name = models.CharField(max_length=100)
    # client_last_name = models.CharField(max_length=100)
    client_address = models.TextField()
    installation_power = models.DecimalField(max_digits=5, decimal_places=2)
    installation_type = models.CharField(max_length=100)

    status = models.CharField(max_length=30, choices=Status.choices, default=Status.TECHNICAL_VISIT)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_installations")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="installations")
    # Utilisateur (installateur) affecté à cette fiche
    affected_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_installations")
    
    # Commissions (copiées depuis le devis)
    commission_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Commission du collaborateur/client (apporteur d'affaires)"
    )
    commission_paid = models.BooleanField(
        default=False,
        help_text="Indique si la commission du collaborateur/client a été payée"
    )
    sales_commission_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Commission du commercial (assigned_to)"
    )
    sales_commission_paid = models.BooleanField(
        default=False,
        help_text="Indique si la commission du commercial a été payée"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_form"
        ordering = ["-created_at"]
        verbose_name = "Fiche d'installation"
        verbose_name_plural = "Fiches d'installation"

    def __str__(self) -> str:
        return f"Fiche {self.id} - {self.created_at.strftime('%Y-%m-%d')}"
    
class TechnicalVisit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="technical_visit")
    visit_date = models.DateField()
    expected_installation_date = models.DateField()
    
    # Informations sur la toiture
    class RoofType(models.TextChoices):
        TILE = "tile", "Tuile"
        SCALE_TILE = "scale_tile", "Tuile écaille"
        SLATE = "slate", "Ardoise"
        STEEL = "steel", "Bac acier"
        FIBROCEMENT = "fibrocement", "Fibrociment"
        FLAT_TERRACE = "flat_terrace", "Toit terrasse"

    roof_type = models.CharField(max_length=20, choices=RoofType.choices, null=True, blank=True)
    tiles_spare_provided = models.BooleanField(default=False)

    class RoofShape(models.TextChoices):
        ONE_SLOPE = "one_slope", "1 pan"
        MULTI_SLOPE = "multi_slope", "Multipan"
        FLAT = "flat", "Toit plat terrasse"

    roof_shape = models.CharField(max_length=20, choices=RoofShape.choices, null=True, blank=True)

    # Accessibilité
    class RoofAccess(models.TextChoices):
        R = "R", "R"
        R1 = "R1", "R1"
        R2 = "R2", "R2"
        OTHER = "other", "Autre"

    roof_access = models.CharField(max_length=10, choices=RoofAccess.choices, null=True, blank=True)
    roof_access_other = models.CharField(max_length=255, blank=True)

    class Ternary(models.TextChoices):
        YES = "yes", "Oui"
        NO = "no", "Non"
        UNKNOWN = "unknown", "Inconnu"

    truck_access = models.CharField(max_length=10, choices=Ternary.choices, default=Ternary.UNKNOWN)
    truck_access_comment = models.TextField(blank=True)

    nacelle_needed = models.CharField(max_length=10, choices=Ternary.choices, default=Ternary.UNKNOWN)

    # Installation électrique existante
    class MeterType(models.TextChoices):
        LINKY = "linky", "Linky"
        OTHER = "other", "Autre"

    meter_type = models.CharField(max_length=10, choices=MeterType.choices, null=True, blank=True)
    meter_type_other = models.CharField(max_length=255, blank=True)

    class CurrentType(models.TextChoices):
        MONO = "mono", "Monophasé"
        TRI = "tri", "Triphasé"

    current_type = models.CharField(max_length=10, choices=CurrentType.choices, null=True, blank=True)
    existing_grid_connection = models.BooleanField(default=True)

    class MeterPosition(models.TextChoices):
        INDOOR = "indoor", "Intérieur"
        OUTDOOR = "outdoor", "Extérieur"
        UNKNOWN = "unknown", "Inconnu"

    meter_position = models.CharField(max_length=10, choices=MeterPosition.choices, default=MeterPosition.UNKNOWN)
    meter_location_photo = models.ImageField(upload_to="installations/technical_visit/meters/", null=True, blank=True)

    # Distance (mètres) entre panneaux et tableau électrique
    panels_to_board_distance_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Matériel supplémentaire
    additional_equipment_needed = models.BooleanField(default=False)
    additional_equipment_details = models.TextField(blank=True, null=True)

    # Validation de la visite technique
    is_validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    approval_statement = models.CharField(max_length=64, default="lu et approuvé")

    # Signatures
    client_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_visit_client"
    )
    installer_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="technical_visit_installer"
    )

    # PDF rapport
    report_pdf = models.FileField(upload_to="installations/technical_visit/reports/", null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_technical_visits")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_technical_visit"
        ordering = ["-visit_date"]
        verbose_name = "Visite technique"
        verbose_name_plural = "Visites techniques"

    def clean(self):
        errors = {}
        if self.roof_access == self.RoofAccess.OTHER and not self.roof_access_other:
            errors["roof_access_other"] = "Veuillez préciser l'accès toiture (Autre)."
        if self.meter_type == self.MeterType.OTHER and not self.meter_type_other:
            errors["meter_type_other"] = "Veuillez préciser le type de compteur (Autre)."
        if self.truck_access == self.Ternary.NO and not self.truck_access_comment:
            errors["truck_access_comment"] = "Veuillez préciser la contrainte d'accès camion."
        if self.additional_equipment_needed and not self.additional_equipment_details:
            errors["additional_equipment_details"] = "Veuillez décrire le matériel supplémentaire nécessaire."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Timestamp lors de la validation
        if self.is_validated and self.validated_at is None:
            from django.utils import timezone
            self.validated_at = timezone.now()
        super().save(*args, **kwargs)

class RepresentationMandate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="representation_mandate")

    # Mandant (Client)
    class Civility(models.TextChoices):
        MME = "mme", "Madame"
        MR = "mr", "Monsieur"

    client_civility = models.CharField(max_length=5, choices=Civility.choices, null=True, blank=True)
    client_birth_date = models.DateField(null=True, blank=True)
    client_birth_place = models.CharField(max_length=255, blank=True)
    client_address = models.TextField(blank=True)  # pré-remplie depuis la fiche client côté appli

    # Mandataire (Installateur)
    company_name = models.CharField(max_length=255, blank=True)
    company_rcs_city = models.CharField(max_length=255, blank=True)  # "Immatriculation au RCS de"
    company_siret = models.CharField(max_length=20, blank=True)
    company_head_office_address = models.TextField(blank=True)
    represented_by = models.CharField(max_length=255, blank=True)
    representative_role = models.CharField(max_length=255, blank=True)

    # Signatures
    client_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="representation_mandate_client"
    )
    installer_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="representation_mandate_installer"
    )

    # PDF mandat généré
    mandate_pdf = models.FileField(upload_to="installations/representation_mandate/pdfs/", null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_representation_mandates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_representation_mandate"
        ordering = ["-created_at"]
        verbose_name = "Mandat de représentation"
        verbose_name_plural = "Mandats de représentation"

class AdministrativeValidation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="administrative_validation")

    # Validation de l'étape
    is_validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_administrative_validations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_administrative_validation"
        ordering = ["-created_at"]
        verbose_name = "Validation administrative"
        verbose_name_plural = "Validations administratives"

    def save(self, *args, **kwargs):
        if self.is_validated and self.validated_at is None:
            from django.utils import timezone
            self.validated_at = timezone.now()
        super().save(*args, **kwargs)

class InstallationCompleted(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="installation_completed")

    # Éléments installés
    modules_installed = models.BooleanField(default=False)
    inverters_installed = models.BooleanField(default=False)  # onduleurs / micro-onduleurs
    dc_ac_box_installed = models.BooleanField(default=False)
    battery_installed = models.BooleanField(default=False)

    # Photos
    photo_modules = models.ImageField(upload_to="installations/completed/modules/", null=True, blank=True)
    photo_inverter = models.ImageField(upload_to="installations/completed/inverter/", null=True, blank=True)

    # PDF rapport
    report_pdf = models.FileField(upload_to="installations/completed/reports/", null=True, blank=True)

    # Signatures
    client_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="installation_completed_client"
    )
    installer_signature = models.OneToOneField(
        Signature, on_delete=models.SET_NULL, null=True, blank=True, related_name="installation_completed_installer"
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_installation_completeds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_completed"
        ordering = ["-created_at"]
        verbose_name = "Installation terminée"
        verbose_name_plural = "Installations terminées"

class ConsuelVisit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="consuel_visit")

    # Résultat de la visite CONSUEL
    passed = models.BooleanField(null=True, blank=True)  # Oui/Non
    refusal_reason = models.TextField(blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_consuel_visits")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_consuel_visit"
        ordering = ["-created_at"]
        verbose_name = "Visite CONSUEL"
        verbose_name_plural = "Visites CONSUEL"

    def clean(self):
        if self.passed is False and not self.refusal_reason:
            raise ValidationError({"refusal_reason": "Le motif du refus est obligatoire lorsque la visite n'est pas validée."})

class EnedisConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="enedis_connection")

    # Validation de l'étape
    is_validated = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_enedis_connections")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_enedis_connection"
        ordering = ["-created_at"]
        verbose_name = "Connexion ENEDIS"
        verbose_name_plural = "Connexions ENEDIS"

    def save(self, *args, **kwargs):
        if self.is_validated and self.validated_at is None:
            from django.utils import timezone
            self.validated_at = timezone.now()
        super().save(*args, **kwargs)

class Commissioning(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name="commissioning")

    # Procès-Verbal remis au client
    handover_receipt_given = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_commissionings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_commissioning"
        ordering = ["-created_at"]
        verbose_name = "Mise en service"
        verbose_name_plural = "Mises en service"


# ==============================
# Documents administratifs (3.2)
# ==============================

## Documents administratifs déplacés dans l'app `administrative`.
