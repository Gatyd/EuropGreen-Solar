from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Form
from .serializers import FormSerializer
from django.db import transaction
from django.core.files.base import ContentFile

from billing.models import Quote
from billing.views import render_quote_pdf
from EuropGreenSolar.email_utils import send_mail
from users.models import User
import secrets, string
from django.utils import timezone


class FormViewSet(viewsets.ModelViewSet):
	queryset = Form.objects.select_related('offer', 'created_by').all()
	serializer_class = FormSerializer
	permission_classes = [permissions.IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(created_by=self.request.user)

	def _generate_password(self, length: int = 12) -> str:
		alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
		return ''.join(secrets.choice(alphabet) for _ in range(length))

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		form: Form = serializer.save(created_by=request.user)

		# Marquer l'offre comme déplacée vers les installations
		offer = form.offer
		offer.installation_moved_at = timezone.now()
		offer.save(update_fields=["installation_moved_at", "updated_at"])

		# 1) Récupérer le dernier devis de l'offre et générer le PDF signé
		quote = Quote.objects.filter(offer=form.offer).order_by('-version').first()
		pdf_attachment = None
		if quote:
			try:
				pdf_bytes = render_quote_pdf(quote)
				if pdf_bytes:
					# Remplacer l'ancien PDF si existant
					if getattr(quote, 'pdf', None):
						try:
							quote.pdf.delete(save=False)
						except Exception:
							pass
					fname = f"devis-{quote.number}.pdf"
					quote.pdf.save(fname, ContentFile(pdf_bytes), save=True)
					pdf_attachment = (fname, pdf_bytes, 'application/pdf')
			except Exception:
				pass

		# 2) Créer un compte client si nécessaire et envoyer l'email d'initiation
		client_email = form.offer.email
		client_first = form.offer.first_name
		client_last = form.offer.last_name
		user = None
		password_for_email = None
		if client_email:
			user = User.objects.filter(email=client_email).first()
			if not user:
				password_for_email = self._generate_password()
				user = User.objects.create_user(
					email=client_email,
					first_name=client_first or '',
					last_name=client_last or '',
					role=User.UserRoles.CUSTOMER,
					password=password_for_email,
				)

		# Email au client
		if client_email:
			ctx = {
				'user': user,
				'password': password_for_email,
				'offer': form.offer,
				'quote': quote,
			}
			attachments = [pdf_attachment] if pdf_attachment else None
			subject = "Votre devis est approuvé – Début des étapes d'installation"
			send_mail(
				template='emails/installation/installation_started.html',
				context=ctx,
				subject=subject,
				to=client_email,
				attachments=attachments,
			)

		headers = self.get_success_headers(self.get_serializer(form).data)
		return Response(self.get_serializer(form).data, status=status.HTTP_201_CREATED, headers=headers)
