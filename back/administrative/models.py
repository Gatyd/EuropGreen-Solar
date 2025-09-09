from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Cerfa16702(models.Model):
    """Déclaration préalable en Mairie (CERFA 16702).

    Contient les champs principaux requis + pièces jointes DPC1..DPC8, DPC11 et signature.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField("installations.Form", on_delete=models.CASCADE, related_name="cerfa16702")

    # 1. Identité du déclarant
    class DeclarantType(models.TextChoices):
        INDIVIDUAL = "individual", "Individu"
        COMPANY = "company", "Entreprise"

    declarant_type = models.CharField(max_length=20, choices=DeclarantType.choices)
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)
    birth_department = models.CharField(max_length=100, blank=True)
    birth_country = models.CharField(max_length=100, blank=True)
    
    # Champs entreprise (si declarant_type = 'company')
    company_denomination = models.CharField(max_length=255, blank=True)
    company_reason = models.CharField(max_length=255, blank=True)
    company_siret = models.CharField(max_length=20, blank=True)
    company_type = models.CharField(max_length=100, blank=True)

    # 2. Coordonnées du déclarant (adresse + contact)
    address_street = models.CharField(max_length=255, blank=True)
    address_number = models.CharField(max_length=30, blank=True)
    address_lieu_dit = models.CharField(max_length=255, blank=True)
    address_locality = models.CharField(max_length=255, blank=True)
    address_postal_code = models.CharField(max_length=10, blank=True)
    address_bp = models.CharField(max_length=20, blank=True)
    address_cedex = models.CharField(max_length=20, blank=True)

    phone_country_code = models.CharField(max_length=5, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    email_consent = models.BooleanField(default=False)

    # 3. Le terrain
    land_street = models.CharField(max_length=255, blank=True)
    land_number = models.CharField(max_length=30, blank=True)
    land_lieu_dit = models.CharField(max_length=255, blank=True)
    land_locality = models.CharField(max_length=255, blank=True)
    land_postal_code = models.CharField(max_length=10, blank=True)

    cadastral_prefix = models.CharField(max_length=10, blank=True)
    cadastral_section = models.CharField(max_length=10, blank=True)
    cadastral_number = models.CharField(max_length=20, blank=True)
    cadastral_surface_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    cadastral_prefix_p2 = models.CharField(max_length=10, blank=True)
    cadastral_section_p2 = models.CharField(max_length=10, blank=True)
    cadastral_number_p2 = models.CharField(max_length=20, blank=True)
    cadastral_surface_m2_p2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    cadastral_prefix_p3 = models.CharField(max_length=10, blank=True)
    cadastral_section_p3 = models.CharField(max_length=10, blank=True)
    cadastral_number_p3 = models.CharField(max_length=20, blank=True)
    cadastral_surface_m2_p3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # 4.1 Le projet
    project_new_construction = models.BooleanField(default=False)
    project_existing_works = models.BooleanField(default=False)
    project_description = models.TextField(blank=True)

    destination_primary_residence = models.BooleanField(default=False)
    destination_secondary_residence = models.BooleanField(default=False)

    agrivoltaic_project = models.BooleanField(default=False)
    electrical_power_text = models.CharField(max_length=100, blank=True)
    peak_power_text = models.CharField(max_length=100, blank=True)
    energy_destination = models.TextField(blank=True)

    # 5. Périmètres de protection
    protection_site_patrimonial = models.BooleanField(default=False)
    protection_site_classe_or_instance = models.BooleanField(default=False)
    protection_monument_abords = models.BooleanField(default=False)

    # 8. Engagement du déclarant
    engagement_city = models.CharField(max_length=100, blank=True)
    engagement_date = models.DateField(default=timezone.now)
    declarant_signature = models.OneToOneField(
        "installations.Signature",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cerfa16702_declarant",
    )

    # Pièces Jointes (DPC)
    dpc1 = models.FileField(upload_to="administrative/cerfa16702/dpc1/", null=True, blank=True)
    dpc2 = models.FileField(upload_to="administrative/cerfa16702/dpc2/", null=True, blank=True)
    dpc3 = models.FileField(upload_to="administrative/cerfa16702/dpc3/", null=True, blank=True)
    dpc4 = models.FileField(upload_to="administrative/cerfa16702/dpc4/", null=True, blank=True)
    dpc5 = models.FileField(upload_to="administrative/cerfa16702/dpc5/", null=True, blank=True)
    dpc6 = models.FileField(upload_to="administrative/cerfa16702/dpc6/", null=True, blank=True)
    dpc7 = models.FileField(upload_to="administrative/cerfa16702/dpc7/", null=True, blank=True)
    dpc8 = models.FileField(upload_to="administrative/cerfa16702/dpc8/", null=True, blank=True)
    dpc11 = models.FileField(upload_to="administrative/cerfa16702/dpc11/", null=True, blank=True)
    dpc11_notice_materiaux = models.TextField(blank=True, null=True)

    # PDF généré
    pdf = models.FileField(upload_to="administrative/cerfa16702/pdfs/", null=True, blank=True)
    attachements_pdf = models.FileField(upload_to="administrative/cerfa16702/attachements_pdfs/", null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_cerfa16702")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "administrative_cerfa16702"
        ordering = ["-created_at"]
        verbose_name = "CERFA 16702"
        verbose_name_plural = "CERFA 16702"


class ElectricalDiagram(models.Model):
    """Document n°2 : Schéma électrique (import PDF ou image)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField("installations.Form", on_delete=models.CASCADE, related_name="electrical_diagram")

    file = models.FileField(upload_to="administrative/electrical_diagrams/", null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_electrical_diagrams")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "administrative_electrical_diagram"
        ordering = ["-created_at"]
        verbose_name = "Schéma électrique"
        verbose_name_plural = "Schémas électriques"


class EnedisMandate(models.Model):
    """Document n°3 : Mandat Enedis (Enedis-FOR-RAC_02E.pdf)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.OneToOneField("installations.Form", on_delete=models.CASCADE, related_name="enedis_mandate")

    # 1. Les parties prenantes — Client
    class ClientType(models.TextChoices):
        INDIVIDUAL = "individual", "Particulier"
        COMPANY = "company", "La société"
        COLLECTIVITY = "collectivity", "Collectivité"

    client_type = models.CharField(max_length=20, choices=ClientType.choices, default=ClientType.INDIVIDUAL)

    class Civility(models.TextChoices):
        MR = "mr", "Monsieur"
        MME = "mme", "Madame"

    client_civility = models.CharField(max_length=5, choices=Civility.choices, null=True, blank=True)

    # Adresse complète du client
    client_address = models.TextField(blank=True)  # pré-remplie depuis le mandat de représentation

    # Si Société/Collectivité
    client_company_name = models.CharField(max_length=255, blank=True)
    client_company_siret = models.CharField(max_length=20, blank=True)
    client_company_represented_by = models.CharField(max_length=255, blank=True)

    # Entreprise qui prend en charge
    contractor_company_name = models.CharField(max_length=255, blank=True)
    contractor_company_siret = models.CharField(max_length=20, blank=True)
    contractor_represented_by_name = models.CharField(max_length=255, blank=True)
    contractor_represented_by_role = models.CharField(max_length=255, blank=True)

    # 2. Le mandat
    class MandateType(models.TextChoices):
        SIMPLE = "simple", "Simple"
        SPECIAL = "special", "Spécial"

    mandate_type = models.CharField(max_length=10, choices=MandateType.choices, default=MandateType.SIMPLE)

    authorize_signature = models.BooleanField(default=False)
    authorize_payment = models.BooleanField(default=False)
    authorize_l342 = models.BooleanField(default=False)
    authorize_network_access = models.BooleanField(default=False)

    # 3. Localisation
    geographic_area = models.CharField(max_length=255, blank=True)

    class ConnectionNature(models.TextChoices):
        INDIV_OR_GROUP_HOUSING = (
            "indiv_or_group_housing",
            "Raccordement de logements individuels ou groupés",
        )
        COMMERCIAL_OR_PRODUCTION = (
            "commercial_or_production",
            "Locaux commerciaux/professionnels ou installation de production",
        )
        BRANCH_MODIFICATION = ("branch_modification", "Modification de branchement")
        POWER_CHANGE_OR_EV = (
            "power_change_or_ev",
            "Modification de la puissance de raccordement / IRVE",
        )

    connection_nature = models.CharField(max_length=40, choices=ConnectionNature.choices, null=True, blank=True)

    # 4. Signatures
    client_signature = models.OneToOneField(
        "installations.Signature",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enedis_mandate_client",
    )
    installer_signature = models.OneToOneField(
        "installations.Signature",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enedis_mandate_installer",
    )

    # PDF
    pdf = models.FileField(upload_to="administrative/enedis_mandate/pdfs/", null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_enedis_mandates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "administrative_enedis_mandate"
        ordering = ["-created_at"]
        verbose_name = "Mandat Enedis"
        verbose_name_plural = "Mandats Enedis"

    def clean(self):
        errors = {}
        if self.client_type in {self.ClientType.COMPANY, self.ClientType.COLLECTIVITY}:
            if not self.client_company_name:
                errors["client_company_name"] = "Nom de l'entreprise requis."
            if not self.client_company_siret:
                errors["client_company_siret"] = "SIRET requis."
            if not self.client_company_represented_by:
                errors["client_company_represented_by"] = "Représentant requis."
        if errors:
            raise ValidationError(errors)
