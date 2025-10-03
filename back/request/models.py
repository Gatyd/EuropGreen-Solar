from django.db import models
from django.conf import settings
import uuid


class ProspectRequest(models.Model):
	class Status(models.TextChoices):
		NEW = "new", "Nouveau"
		FOLLOWUP = "followup", "À relancer"
		INFO = "info", "Demande de renseignement"
		IN_PROGRESS = "in_progress", "En cours"
		CLOSED = "closed", "Clôturé"

	class Source(models.TextChoices):
		CALL_CENTER = "call_center", "Call Center"
		WEB_FORM = "web_form", "Formulaire de demande"
		CLIENT = "client", "Client"
		COLLABORATOR = "collaborator", "Collaborateur"
		COMMERCIAL = "commercial", "Commercial"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	last_name = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	address = models.CharField(max_length=255)
	housing_type = models.CharField(max_length=100, blank=True)
	electricity_bill = models.FileField(upload_to="requests/bills/", blank=True, null=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
	source_type = models.CharField(max_length=20, choices=Source.choices, default=Source.WEB_FORM)
	source = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="prospect_sources")
	appointment_date = models.DateTimeField(null=True)
	converted_to_offer_at = models.DateTimeField(null=True, blank=True)
	# Indique la décision finale lorsque le statut est clôturé:
	#   True  -> prospect validé (converti potentiellement)
	#   False -> prospect abandonné
	#   None  -> décision non encore prise (afficher boutons choix)
	converted_decision = models.BooleanField(null=True, blank=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_requests")
	assigned_to = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="assigned_requests",
	)
	# notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "requests_prospect"
		ordering = ["-created_at"]
		verbose_name = "Demande"
		verbose_name_plural = "Demandes"

	def __str__(self) -> str:
		return f"{self.last_name} {self.first_name} - {self.get_status_display}"
