from django.db import models
from django.conf import settings
import uuid

class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer = models.OneToOneField("offers.Offer", on_delete=models.CASCADE, related_name="installations_form")
    client_first_name = models.CharField(max_length=100)
    client_last_name = models.CharField(max_length=100)
    client_address = models.TextField()
    installation_power = models.DecimalField(max_digits=5, decimal_places=2)
    installation_type = models.CharField(max_length=100)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_installations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installations_form"
        ordering = ["-created_at"]
        verbose_name = "Fiche d'installation"
        verbose_name_plural = "Fiches d'installation"

    def __str__(self) -> str:
        return f"Fiche {self.id} - {self.created_at.strftime('%Y-%m-%d')}"