from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Form
from .serializers import FormSerializer, FormDetailSerializer, TechnicalVisitSerializer
from django.db import transaction
from django.core.files.base import ContentFile

from billing.models import Quote
from billing.views import render_quote_pdf
from EuropGreenSolar.email_utils import send_mail
from users.models import User
import secrets, string
from django.utils import timezone
from authentication.permissions import HasInstallationAccess
from .models import TechnicalVisit, Signature
import base64
import re


class FormViewSet(viewsets.ModelViewSet):
	queryset = Form.objects.select_related('offer', 'created_by').all()
	serializer_class = FormSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		qs = Form.objects.select_related('offer', 'created_by', 'client')
		user = getattr(self.request, 'user', None)
		if not user or not user.is_authenticated:
			return qs.none()
		if user.is_superuser:
			# Administrateur: toutes les fiches
			return qs
		if user.is_staff:
			# Employé: uniquement celles qu'il a créées
			return qs.filter(created_by=user)
		# Client: uniquement celles où il est client
		return qs.filter(client=user)

	def get_permissions(self):
		user = getattr(self.request, 'user', None)
		if user and user.is_authenticated and user.is_staff:
			permission_classes = [HasInstallationAccess]
		else:
			permission_classes = [permissions.IsAuthenticated]
		return [p() for p in permission_classes]

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
			# Si le modèle a un champ client, lier l'utilisateur (optionnel)
			if hasattr(form, 'client'):
				form.client = user
				form.save(update_fields=['client', 'updated_at'])

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

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = FormDetailSerializer(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	# --- Actions personnalisées ---

	def _decode_data_url_image(self, data_url: str):
		"""Retourne (ContentFile, ext) à partir d'une data URL d'image, sinon (None, None)."""
		if not data_url or not isinstance(data_url, str):
			return None, None
		match = re.match(r"^data:image/(png|jpeg|jpg);base64,(.+)$", data_url)
		if not match:
			return None, None
		ext = match.group(1)
		b64 = match.group(2)
		try:
			decoded = base64.b64decode(b64)
			return ContentFile(decoded), ext
		except Exception:
			return None, None

	def _get_client_ip(self, request):
		xff = request.META.get('HTTP_X_FORWARDED_FOR')
		if xff:
			return xff.split(',')[0].strip()
		return request.META.get('REMOTE_ADDR')

	@action(detail=True, methods=['post'], url_path='technical-visit')
	@transaction.atomic
	def create_or_update_technical_visit(self, request, pk=None):
		"""Créer ou mettre à jour la visite technique de la fiche.

		Attend des champs correspondant aux choix du modèle (codes), p.ex. roof_type=tile, meter_type=linky, etc.
		Peut recevoir un fichier 'meter_location_photo'.
		"""
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'technical_visit') or form.technical_visit is None
		
		if is_create:
			tv = TechnicalVisit(form=form, created_by=request.user)
		else:
			tv = form.technical_visit  # type: ignore

		# Mapping simple des champs
		field_map = {
			'visit_date': 'visit_date',
			'expected_installation_date': 'expected_installation_date',
			'roof_type': 'roof_type',
			'tiles_spare_provided': 'tiles_spare_provided',
			'roof_shape': 'roof_shape',
			'roof_access': 'roof_access',
			'roof_access_other': 'roof_access_other',
			'nacelle_needed': 'nacelle_needed',
			'truck_access': 'truck_access',
			'truck_access_comment': 'truck_access_comment',
			'meter_type': 'meter_type',
			'meter_type_other': 'meter_type_other',
			'current_type': 'current_type',
			'existing_grid_connection': 'existing_grid_connection',
			'meter_position': 'meter_position',
			'panels_to_board_distance_m': 'panels_to_board_distance_m',
			'additional_equipment_needed': 'additional_equipment_needed',
			'additional_equipment_details': 'additional_equipment_details',
		}
		for src, dst in field_map.items():
			if src in payload:
				setattr(tv, dst, payload.get(src))

		# Fichier photo éventuel
		photo = request.FILES.get('meter_location_photo')
		if photo:
			tv.meter_location_photo = photo

		# Éventuelle signature installateur à la création
		if is_create:
			ins_name = (payload.get('installer_signer_name') or '').strip()
			file = request.FILES.get('installer_signature_file')
			data_url = payload.get('installer_signature_data')
			if ins_name and (file or data_url):
				sig = Signature(
					signer_name=ins_name,
					ip_address=self._get_client_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
				)
				if file:
					sig.signature_image = file
				else:
					cf, ext = self._decode_data_url_image(str(data_url))
					if cf:
						sig.signature_image.save(f"signature.{ext or 'png'}", cf, save=False)
				sig.save()
				tv.installer_signature = sig

		# Validation et sauvegarde
		tv.full_clean()
		tv.save()

		# Email d'information au client (best-effort, non bloquant)
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'technical_visit': tv,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_signature': f"{request.scheme}://{request.get_host()}/home/installations/{form.id}",
				}
				subject = "Visite technique effectuée – Signature requise"
				send_mail(
					template='emails/installation/technical_visit_signature_pending.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

		serializer = TechnicalVisitSerializer(tv, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='technical-visit/sign')
	@transaction.atomic
	def sign_technical_visit(self, request, pk=None):
		"""Enregistrer une signature (client ou installateur) pour la visite technique.

		Payload:
		- role: 'client' | 'installer' (optionnel; sinon déduit du rôle utilisateur)
		- signer_name: str
		- signature_file: fichier image (optionnel)
		- signature_data: data URL d'une image (optionnel)
		"""
		form = self.get_object()
		if not hasattr(form, 'technical_visit') or form.technical_visit is None:
			return Response({ 'detail': "Aucune visite technique n'est associée à cette fiche." }, status=status.HTTP_400_BAD_REQUEST)
		tv: TechnicalVisit = form.technical_visit  # type: ignore

		role = (request.data.get('role') or '').strip().lower()
		if role not in ('client', 'installer'):
			# Déduction basique: client si non staff, sinon installateur
			role = 'installer' if getattr(request.user, 'is_staff', False) else 'client'

		signer_name = (request.data.get('signer_name') or '').strip()
		if not signer_name:
			return Response({ 'signer_name': 'Ce champ est requis.' }, status=status.HTTP_400_BAD_REQUEST)

		# Construire l'objet Signature
		sig = Signature(
			signer_name=signer_name,
			ip_address=self._get_client_ip(request),
			user_agent=request.META.get('HTTP_USER_AGENT', ''),
		)
		file = request.FILES.get('signature_file')
		if file:
			sig.signature_image = file
		else:
			data_url = request.data.get('signature_data')
			cf, ext = self._decode_data_url_image(data_url)
			if cf:
				# Nom par défaut
				sig.signature_image.save(f"signature.{ext or 'png'}", cf, save=False)

		sig.save()

		# Affecter la signature au bon champ
		if role == 'client':
			# Remplacer la signature existante si besoin
			if tv.client_signature_id:
				try:
					old = tv.client_signature
					if old and old.signature_image:
						old.signature_image.delete(save=False)
				except Exception:
					pass
			tv.client_signature = sig
		else:
			if tv.installer_signature_id:
				try:
					old = tv.installer_signature
					if old and old.signature_image:
						old.signature_image.delete(save=False)
				except Exception:
					pass
			tv.installer_signature = sig

		tv.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])

		serializer = TechnicalVisitSerializer(tv, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_200_OK)
