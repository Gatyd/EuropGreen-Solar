from django.db import models
from django.conf import settings
import uuid


class Offer(models.Model):
	class Status(models.TextChoices):
		TO_CONTACT = "to_contact", "À contacter"
		PHONE_MEETING = "phone_meeting", "Rendez-vous Téléphonique"
		MEETING = "meeting", "Rendez-vous physique/Visio"
		QUOTE_SENT = "quote_sent", "Devis envoyé"
		NEGOTIATION = "negotiation", "Négociation/questions"
		QUOTE_SIGNED = "quote_signed", "Devis signé"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	request = models.OneToOneField('request.ProspectRequest', on_delete=models.CASCADE, related_name='offer')

	# Données client (pré-remplies depuis la demande)
	last_name = models.CharField(max_length=100)
	first_name = models.CharField(max_length=100)
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	address = models.CharField(max_length=255)
	# housing_type = models.CharField(max_length=100, blank=True)

	# Détails projet (placeholder libre pour le moment)
	project_details = models.TextField(blank=True)

	status = models.CharField(max_length=20, choices=Status.choices, default=Status.TO_CONTACT)

	# Date/heure à laquelle l'offre a été déplacée vers les installations
	installation_moved_at = models.DateTimeField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "offers_offer"
		ordering = ["-created_at"]
		verbose_name = "Offre"
		verbose_name_plural = "Offres"

	def __str__(self) -> str:
		return f"Offre {self.last_name} {self.first_name} - {self.get_status_display()}"
