from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    Form, TechnicalVisit, Signature, RepresentationMandate, AdministrativeValidation,
	InstallationCompleted, ConsuelVisit, EnedisConnection, Commissioning
)
from .serializers import (
	FormSerializer, FormDetailSerializer, TechnicalVisitSerializer, RepresentationMandateSerializer,
	AdministrativeValidationSerializer, InstallationCompletedSerializer, ConsuelVisitSerializer, EnedisConnectionSerializer, CommissioningSerializer
)
from django.db import transaction
from django.core.files.base import ContentFile
from EuropGreenSolar.utils.helpers import get_client_ip, decode_data_url_image
from billing.models import Quote
from billing.views import render_quote_pdf
from EuropGreenSolar.email_utils import send_mail
from users.models import User
import secrets, string
from django.utils import timezone
from authentication.permissions import HasInstallationAccess
from administrative.models import EnedisMandate
from administrative.serializers import EnedisMandateSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q


class FormViewSet(viewsets.ModelViewSet):
	queryset = Form.objects.select_related('offer', 'created_by').all()
	serializer_class = FormSerializer
	permission_classes = [permissions.IsAuthenticated]

	# ----------------------
	# Helpers internes
	# ----------------------

	def _get_client_email(self, form: Form):
		try:
			return form.client.email if getattr(form, 'client', None) else form.offer.email
		except Exception:
			return None

	def _get_client_name(self, form: Form) -> str:
		client = getattr(form, 'client', None)
		first = getattr(client, 'first_name', '')
		last = getattr(client, 'last_name', '')
		return f"{first} {last}".strip()

	def _send_mail_safe(self, *, template: str, context: dict, subject: str, to: str, attachments=None, save_to_log=True):
		try:
			if to:
				send_mail(
					template=template,
					context=context,
					subject=subject,
					to=to,
					attachments=attachments,
					save_to_log=save_to_log,
				)
		except Exception:
			# best-effort: ne pas bloquer le flux en cas d'erreur d'email
			pass

	def _map_fields(self, instance, payload: dict, field_list: list[str]):
		for field in field_list:
			if field in payload:
				setattr(instance, field, payload.get(field))

	def _update_file_fields(self, instance, files_dict, file_fields: list[str]):
		for f in file_fields:
			if f in files_dict:
				setattr(instance, f, files_dict[f])

	def _build_signature_from_request(self, request, *, signer_name: str, file_key: str, data_key: str, filename_base: str):
		signer_name = (signer_name or '').strip()
		file = request.FILES.get(file_key)
		data_url = request.data.get(data_key)
		if not signer_name or not (file or data_url):
			return None
		sig = Signature(
			signer_name=signer_name,
			ip_address=get_client_ip(request),
			user_agent=request.META.get('HTTP_USER_AGENT', ''),
		)
		if file:
			sig.signature_image = file
		else:
			try:
				cf, ext = decode_data_url_image(str(data_url))
				if cf:
					sig.signature_image.save(f"{filename_base}.{ext or 'png'}", cf, save=False)
			except Exception:
				pass
		sig.save()
		return sig

	def _replace_signature(self, target, field_name: str, sig: Signature):
		# field_name: 'client_signature' | 'installer_signature'
		try:
			if getattr(target, f"{field_name}_id", None):
				old = getattr(target, field_name)
				if old and getattr(old, 'signature_image', None):
					try:
						old.signature_image.delete(save=False)
					except Exception:
						pass
		except Exception:
			pass
		setattr(target, field_name, sig)

	def _both_signed(self, obj) -> bool:
		return bool(getattr(obj, 'client_signature_id', None) and getattr(obj, 'installer_signature_id', None))

	def _queue_pdf_generation(self, form: Form, doc: str):
		# doc in ('technical_visit', 'representation_mandate', 'enedis_mandate', 'installation_completed')
		mapping = {
			'technical_visit': {
				'related': 'technical_visit',
				'renderer': 'render_technical_visit_pdf',
				'filename': 'visite_technique_{fid}.pdf',
				'fileattr': 'report_pdf',
			},
			'representation_mandate': {
				'related': 'representation_mandate',
				'renderer': 'render_representation_mandate_pdf',
				'filename': 'mandat_de_representation_{fid}.pdf',
				'fileattr': 'mandate_pdf',
			},
			'enedis_mandate': {
				'related': 'enedis_mandate',
				'renderer': 'render_enedis_mandate_pdf',
				'filename': 'mandat_enedis_{fid}.pdf',
				'fileattr': 'pdf',
			},
			'installation_completed': {
				'related': 'installation_completed',
				'renderer': 'render_installation_completed_pdf',
				'filename': 'rapport_installation_{fid}.pdf',
				'fileattr': 'report_pdf',
			},
		}
		if doc not in mapping:
			return
		cfg = mapping[doc]

		def _gen_pdf_after_commit(fid: str, related: str, renderer_name: str, filename_tpl: str, fileattr: str):
			try:
				from .models import Form as _Form
				from . import pdf as _pdf
				f = _Form.objects.select_related(related).get(pk=fid)
				renderer = getattr(_pdf, renderer_name, None)
				if not renderer:
					return
				pdf_bytes = renderer(str(fid))
				if pdf_bytes and getattr(f, related, None):
					filename = filename_tpl.format(fid=fid)
					try:
						target_obj = getattr(f, related)
						filefield = getattr(target_obj, fileattr)
						filefield.save(filename, ContentFile(pdf_bytes), save=True)
					except Exception:
						pass
			except Exception:
				pass

		transaction.on_commit(lambda fid=str(str(form.id).split('-')[0]), related=cfg['related'], renderer=cfg['renderer'], fname=cfg['filename'], fattr=cfg['fileattr']: _gen_pdf_after_commit(fid, related, renderer, fname, fattr))

	def get_queryset(self):
		qs = Form.objects.select_related('offer', 'created_by', 'client')
		if getattr(self, 'action', None) == 'retrieve':
			return qs
		user = getattr(self.request, 'user', None)
		if not user or not user.is_authenticated:
			return qs.none()
		# Base permissions
		if user.is_superuser:
			base_qs = qs
		elif user.is_staff:
			base_qs = qs.filter(
				Q(created_by=user) | Q(affected_user=user) |
				Q(offer__request__source=user) | Q(offer__request__assigned_to=user)
			)
		else:
			base_qs = qs.filter(client=user)

		# Filtres optionnels via query params
		params = self.request.query_params
		client_param = params.get('client') or params.get('client_id')
		created_by_param = params.get('created_by')
		affected_user_param = params.get('affected_user')

		# Filtre client (ET)
		if client_param:
			try:
				base_qs = base_qs.filter(client_id=client_param)
			except Exception:
				pass

		# Filtre créé par / affecté à (OU si les deux sont fournis)
		if created_by_param and affected_user_param:
			base_qs = base_qs.filter(Q(created_by_id=created_by_param) | Q(affected_user_id=affected_user_param))
		elif created_by_param:
			base_qs = base_qs.filter(created_by_id=created_by_param)
		elif affected_user_param:
			base_qs = base_qs.filter(affected_user_id=affected_user_param)

		return base_qs

	def get_permissions(self):
		action = getattr(self, 'action', None)
		user = getattr(self.request, 'user', None)
		
		# retrieve est public (AllowAny)
		if action == 'retrieve':
			return [permissions.AllowAny()]
		
		# Si l'utilisateur est staff ou superuser : permissions normales avec HasInstallationAccess
		if user and user.is_authenticated and (user.is_staff or user.is_superuser):
			return [HasInstallationAccess()]
		
		# Si l'utilisateur est un client (authentifié mais pas staff) : 
		# limiter aux actions autorisées (list, retrieve, sign_document)
		if user and user.is_authenticated:
			allowed_client_actions = ['list', 'retrieve', 'sign_document']
			if action not in allowed_client_actions:
				# Retourner une permission qui refuse toujours l'accès
				return [permissions.IsAdminUser()]
			return [permissions.IsAuthenticated()]
		
		# Par défaut : utilisateur non authentifié
		return [permissions.IsAuthenticated()]

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
			# Copier les commissions du devis vers la fiche d'installation
			form.commission_amount = quote.commission_amount or 0
			form.sales_commission_amount = quote.sales_commission_amount or 0
			form.save(update_fields=['commission_amount', 'sales_commission_amount', 'updated_at'])
			
			try:
				pdf_bytes = render_quote_pdf(quote)
				if pdf_bytes:
					# Remplacer l'ancien PDF si existant
					if getattr(quote, 'pdf', None):
						try:
							quote.pdf.delete(save=False)
						except Exception:
							pass
					fname = f"{quote.number}.pdf"
					quote.pdf.save(fname, ContentFile(pdf_bytes), save=True)
					pdf_attachment = (fname, pdf_bytes, 'application/pdf')
			except Exception:
				pass
		# 2) Créer un compte client si nécessaire et envoyer l'email d'initiation
		# Rafraîchir l'offre depuis la DB pour avoir les dernières valeurs
		offer.refresh_from_db()
		client_email = offer.email
		client_first = offer.first_name
		client_last = offer.last_name
		client_phone = offer.phone
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
					phone_number=client_phone or '',
					role=User.UserRoles.CUSTOMER,
					password=password_for_email,
				)
			# Si le modèle a un champ client, lier l'utilisateur (optionnel)
			if hasattr(form, 'client'):
				form.client = user
				form.save(update_fields=['client', 'updated_at'])

			# Email au client
			ctx = {
				'user': user,
				'password': password_for_email,
				'offer': form.offer,
				'quote': quote,
			}
			attachments = [pdf_attachment] if pdf_attachment else None
			subject = "Votre devis est approuvé – Début des étapes d'installation"
			self._send_mail_safe(
				template='emails/installation/installation_started.html',
				context=ctx,
				subject=subject,
				to=client_email,
				attachments=attachments,
				save_to_log=False,  # Ne pas enregistrer car contient un mot de passe
			)
		headers = self.get_success_headers(self.get_serializer(form).data)
		return Response(self.get_serializer(form).data, status=status.HTTP_201_CREATED, headers=headers)

	@action(detail=True, methods=['post'], url_path='assign-installer')
	def assign_installer(self, request, pk=None):
		"""Affecte un installateur (affected_user) à la fiche et notifie par email."""
		form = self.get_object()
		installer_id = request.data.get('installer_id')
		if not installer_id:
			return Response({'installer_id': 'Ce champ est requis.'}, status=status.HTTP_400_BAD_REQUEST)
		installer = get_object_or_404(User, pk=installer_id)
		# Optionnel: restreindre aux rôles autorisés
		if installer.role not in [User.UserRoles.INSTALLER]:
			return Response({'detail': "L'utilisateur sélectionné n'est pas un installateur valide."}, status=status.HTTP_400_BAD_REQUEST)
		form.affected_user = installer
		form.save(update_fields=['affected_user', 'updated_at'])
		# Envoi de l'email à l'installateur
		context = {
			'installer': installer,
			'form': form,
			'client_name': self._get_client_name(form),
			'link_installation': f"/home/installations/{form.id}",
		}
		try:
			send_mail(
				template='emails/installation/installer_assigned.html',
				context=context,
				subject="Nouvelle installation assignée",
				to=installer.email,
			)
		except Exception:
			pass
		return Response({'status': 'assigned', 'installer_id': str(installer.id)}, status=status.HTTP_200_OK)

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = FormDetailSerializer(instance, context=self.get_serializer_context())
		return Response(serializer.data)

	@action(detail=True, methods=['post'], url_path='technical-visit')
	@transaction.atomic
	def create_or_update_technical_visit(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'technical_visit') or form.technical_visit is None
		
		if is_create:
			tv = TechnicalVisit(form=form, created_by=request.user)
		else:
			tv = form.technical_visit  # type: ignore

		# Mapping simple des champs
		field_list = [
			'visit_date', 'expected_installation_date', 'roof_type', 'tiles_spare_provided', 'roof_shape', 'roof_access',
			'roof_access_other', 'nacelle_needed', 'truck_access', 'truck_access_comment', 'meter_type', 'meter_type_other',
			'current_type', 'existing_grid_connection', 'meter_position', 'panels_to_board_distance_m', 'additional_equipment_needed',
			'additional_equipment_details'
		]
		self._map_fields(tv, payload, field_list)
		# Fichier photo éventuel
		photo = request.FILES.get('meter_location_photo')
		if photo:
			tv.meter_location_photo = photo
		# Éventuelle signature installateur à la création
		if is_create:
			sig = self._build_signature_from_request(
				request, signer_name=payload.get('installer_signer_name'), file_key='installer_signature_file',
				data_key='installer_signature_data', filename_base=f"installer-signature-technical_visit-{tv.id}",
			)
			if sig:
				tv.installer_signature = sig
		# Validation et sauvegarde
		tv.full_clean()
		tv.save()
		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = { 'form': form, 'technical_visit': tv, 'client_name': self._get_client_name(form),
			'link_signature': f"/home/installations/{form.id}?action=sign-technical-visit",
		}
		subject = "Visite technique effectuée – Signature requise"
		self._send_mail_safe(
			template='emails/installation/technical_visit_signature_pending.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = TechnicalVisitSerializer(tv, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='sign')
	@transaction.atomic
	def sign_document(self, request, pk=None):
		form = self.get_object()
		doc = (request.data.get('document') or '').strip().lower()
		if doc not in ('technical_visit', 'representation_mandate', 'enedis_mandate', 'installation_completed'):
			return Response({ 'document': 'Type de document non supporté.' }, status=status.HTTP_400_BAD_REQUEST)

		# Récupérer l'instance cible
		target = None
		if doc == 'technical_visit':
			target = getattr(form, 'technical_visit', None)
		elif doc == 'representation_mandate':
			target = getattr(form, 'representation_mandate', None)
		elif doc == 'enedis_mandate':
			target = getattr(form, 'enedis_mandate', None)
		elif doc == 'installation_completed':
			target = getattr(form, 'installation_completed', None)

		if target is None:
			return Response({ 'detail': "Aucun objet n'est associé à cette fiche pour ce document." }, status=status.HTTP_400_BAD_REQUEST)

		role = (request.data.get('role') or '').strip().lower()
		if role not in ('client', 'installer'):
			role = 'installer' if getattr(request.user, 'is_staff', False) else 'client'

		signer_name = (request.data.get('signer_name') or '').strip()
		if not signer_name:
			return Response({ 'signer_name': 'Ce champ est requis.' }, status=status.HTTP_400_BAD_REQUEST)

		sig = self._build_signature_from_request(
			request, signer_name=signer_name, file_key='signature_file',
			data_key='signature_data', filename_base=f"{role}-signature-{doc}-{form.id}",
		)

		# Affectation selon le type
		if doc == 'technical_visit':
			tv: TechnicalVisit = target
			field = 'client_signature' if role == 'client' else 'installer_signature'
			self._replace_signature(tv, field, sig)
			tv.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])
			# Génération PDF si complet (après COMMIT)
			if self._both_signed(tv):
				self._queue_pdf_generation(form, 'technical_visit')
			serializer = TechnicalVisitSerializer(tv, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)

		elif doc == 'representation_mandate':
			rm: RepresentationMandate = target
			field = 'client_signature' if role == 'client' else 'installer_signature'
			self._replace_signature(rm, field, sig)
			rm.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])
			if self._both_signed(rm):
				self._queue_pdf_generation(form, 'representation_mandate')
			serializer = RepresentationMandateSerializer(rm, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)

		elif doc == 'enedis_mandate':
			em: EnedisMandate = target
			field = 'client_signature' if role == 'client' else 'installer_signature'
			self._replace_signature(em, field, sig)
			em.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])
			if self._both_signed(em):
				self._queue_pdf_generation(form, 'enedis_mandate')
			serializer = EnedisMandateSerializer(em, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)
		
		elif doc == 'installation_completed':
			ic: InstallationCompleted = target
			field = 'client_signature' if role == 'client' else 'installer_signature'
			self._replace_signature(ic, field, sig)
			ic.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])
			if self._both_signed(ic):
				self._queue_pdf_generation(form, 'installation_completed')
			serializer = InstallationCompletedSerializer(ic, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)


	@action(detail=True, methods=['post'], url_path='representation-mandate')
	@transaction.atomic
	def create_or_update_representation_mandate(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'representation_mandate') or form.representation_mandate is None
		
		if is_create:
			rm = RepresentationMandate(form=form, created_by=request.user)
		else:
			rm = form.representation_mandate  # type: ignore

		# Mapping simple des champs
		field_list = ['client_civility', 'client_birth_date', 'client_birth_place', 'client_address', 'company_name', 
			'company_rcs_city', 'company_siret', 'company_head_office_address', 'represented_by', 'representative_role'
		]
		self._map_fields(rm, payload, field_list)
		# Éventuelle signature installateur à la création
		if is_create:
			sig = self._build_signature_from_request(
				request, signer_name=payload.get('installer_signer_name'), file_key='installer_signature_file',
				data_key='installer_signature_data', filename_base=f"installer-signature-representation_mandate-{rm.id}",
			)
			if sig:
				rm.installer_signature = sig
		# Validation et sauvegarde
		rm.full_clean()
		rm.save()
		form.status = 'representation_mandate'
		form.save()
		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = {
			'form': form, 'representation_mandate': rm, 'client_name': self._get_client_name(form),
			'link_signature': f"/home/installations/{form.id}?action=sign-representation-mandate",
		}
		subject = "Mandat de représentation créé – Signature requise"
		self._send_mail_safe(
			template='emails/installation/representation_mandate_signature_pending.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = RepresentationMandateSerializer(rm, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)
	
	@action(detail=True, methods=['post'], url_path='enedis-mandate')
	@transaction.atomic
	def create_or_update_enedis_mandate(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'enedis_mandate') or form.enedis_mandate is None
		
		if is_create:
			em = EnedisMandate(form=form, created_by=request.user)
		else:
			em = form.enedis_mandate  # type: ignore

		# Mapping simple des champs
		field_list = ['client_name', 'client_type', 'client_civility', 'client_address', 'client_company_name', 'client_company_siret', 'client_company_represented_by_name', 'client_company_represented_by_role',
			'contractor_name', 'contractor_type', 'contractor_civility', 'contractor_address', 'contractor_company_name', 'contractor_company_siret', 'contractor_company_represented_by_name', 'contractor_company_represented_by_role',
			'mandate_type', 'authorize_signature', 'authorize_payment', 'authorize_l342', 'authorize_network_access', 'geographic_area', 'connection_nature', 'client_location', 'installer_location'
		]
		self._map_fields(em, payload, field_list)
		# Éventuelle signature installateur à la création
		if is_create:
			sig = self._build_signature_from_request(
				request, signer_name=payload.get('installer_signer_name'), file_key='installer_signature_file',
				data_key='installer_signature_data', filename_base=f"installer-signature-enedis_mandate-{em.id}",
			)
			if sig:
				em.installer_signature = sig
		# Validation et sauvegarde
		em.full_clean()
		em.save()
		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = {
			'form': form, 'enedis_mandate': em, 'client_name': self._get_client_name(form),
			'link_signature': f"/home/installations/{form.id}?action=sign-enedis-mandate",
		}
		subject = "Mandat Enedis créé – Signature requise"
		self._send_mail_safe(
			template='emails/installation/enedis_mandate_signature_pending.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = EnedisMandateSerializer(em, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)
	
	@action(detail=True, methods=['post'], url_path='administrative-validation')
	@transaction.atomic
	def create_or_update_administrative_validation(self, request, pk=None):
		form = self.get_object()
		is_create = not hasattr(form, 'administrative_validation') or form.administrative_validation is None

		if is_create:
			av = AdministrativeValidation(form=form, created_by=request.user)
		else:
			av = form.administrative_validation  # type: ignore

		av.is_validated = True
		av.save()
		form.status = 'administrative_validation'
		form.save()

		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = {
			'form': form, 'client_name': self._get_client_name(form),
			'link_installation': f"/home/installations/{form.id}",
		}
		subject = "Démarches administratives validées"
		self._send_mail_safe(
			template='emails/installation/administrative_validated.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = AdministrativeValidationSerializer(av, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)
	
	@action(detail=True, methods=['post'], url_path='installation-completed')
	@transaction.atomic
	def create_or_update_installation(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'installation_completed') or form.installation_completed is None

		if is_create:
			ic = InstallationCompleted(form=form, created_by=request.user)
		else:
			ic = form.installation_completed  # type: ignore

		# Mapping simple des champs
		field_list = ['modules_installed', 'inverters_installed', 'dc_ac_box_installed', 'battery_installed']
		file_list = ['photo_modules', 'photo_inverter']
		self._map_fields(ic, payload, field_list)
		self._update_file_fields(ic, request.FILES, file_list)
		# Éventuelle signature installateur à la création
		if is_create:
			sig = self._build_signature_from_request(
				request, signer_name=payload.get('installer_signer_name'), file_key='installer_signature_file',
				data_key='installer_signature_data', filename_base=f"installer-signature-installation_completed-{ic.id}",
			)
			if sig:
				ic.installer_signature = sig
		# Validation et sauvegarde
		ic.full_clean()
		ic.save()
		form.status = 'installation_completed'
		form.save()
		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = {
			'form': form, 'installation_completed': ic, 'client_name': self._get_client_name(form),
			'link_signature': f"/home/installations/{form.id}?action=sign-installation-completed",
		}
		subject = "Installation terminée – Signature requise"
		self._send_mail_safe(
			template='emails/installation/installation_completed_signature_pending.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = InstallationCompletedSerializer(ic, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='consuel-visit')
	@transaction.atomic
	def create_or_update_consuel_visit(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'consuel_visit') or form.consuel_visit is None

		if is_create:
			cv = ConsuelVisit(form=form, created_by=request.user)
		else:
			cv = form.consuel_visit  # type: ignore

		field_list = ['passed', 'refusal_reason']
		for field in field_list:
			if field in payload:
				setattr(cv, field, payload.get(field))

		cv.full_clean()
		cv.save()
		form.status = 'consuel_visit'
		form.save()

		# Email d'information au client (best-effort, non bloquant)
		if cv.passed:
			client_email = self._get_client_email(form)
			ctx = {
				'form': form, 'client_name': self._get_client_name(form),
				'link_installation': f"/home/installations/{form.id}",
			}
			subject = "Conformité CONSUEL enregistrée"
			self._send_mail_safe(
				template='emails/installation/consuel_visit.html',
				context=ctx, subject=subject, to=client_email,
			)

		serializer = ConsuelVisitSerializer(cv, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='enedis-connection')
	@transaction.atomic
	def create_or_update_enedis_connection(self, request, pk=None):
		form = self.get_object()
		is_create = not hasattr(form, 'enedis_connection') or form.enedis_connection is None

		if is_create:
			ec = EnedisConnection(form=form, created_by=request.user)
		else:
			ec = form.enedis_connection  # type: ignore

		ec.is_validated = True
		ec.save()
		form.status = 'enedis_connection'
		form.save()

		# Email d'information au client (best-effort, non bloquant)
		client_email = self._get_client_email(form)
		ctx = {
			'form': form, 'client_name': self._get_client_name(form),
			'link_installation': f"/home/installations/{form.id}",
		}
		subject = "Raccordement ENEDIS validé"
		self._send_mail_safe(
			template='emails/installation/enedis_connection_validated.html',
			context=ctx, subject=subject, to=client_email,
		)

		serializer = EnedisConnectionSerializer(ec, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='commissioning')
	@transaction.atomic
	def create_or_update_commissioning(self, request, pk=None):
		form = self.get_object()
		payload = request.data
		is_create = not hasattr(form, 'commissioning') or form.commissioning is None

		if is_create:
			cm = Commissioning(form=form, created_by=request.user)
		else:
			cm = form.commissioning  # type: ignore

		if 'handover_receipt_given' in payload:
			cm.handover_receipt_given = payload['handover_receipt_given']

		cm.save()
		form.status = 'commissioning'
		form.save()

		# Email d'information au client (best-effort, non bloquant)
		if cm.handover_receipt_given:
			client_email = self._get_client_email(form)
			ctx = {
				'form': form, 'client_name': self._get_client_name(form),
				'link_installation': f"/home/installations/{form.id}",
			}
			subject = "Mise en service effectuée"
			self._send_mail_safe(
				template='emails/installation/commissioning.html',
				context=ctx, subject=subject, to=client_email,
			)

		serializer = CommissioningSerializer(cm, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)
	