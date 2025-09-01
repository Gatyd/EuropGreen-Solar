from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    Form, TechnicalVisit, Signature, RepresentationMandate, AdministrativeValidation,
	InstallationCompleted, ConsuelVisit, EnedisConnection
)
from .serializers import (
	FormSerializer, FormDetailSerializer, TechnicalVisitSerializer, RepresentationMandateSerializer,
	AdministrativeValidationSerializer, InstallationCompletedSerializer, ConsuelVisitSerializer, EnedisConnectionSerializer
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


class FormViewSet(viewsets.ModelViewSet):
	queryset = Form.objects.select_related('offer', 'created_by').all()
	serializer_class = FormSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		qs = Form.objects.select_related('offer', 'created_by', 'client')
		if getattr(self, 'action', None) == 'retrieve':
			return qs
		user = getattr(self.request, 'user', None)
		if not user or not user.is_authenticated:
			return qs.none()
		if user.is_superuser:
			return qs
		if user.is_staff:
			return qs.filter(created_by=user)
		return qs.filter(client=user)

	def get_permissions(self):
		if getattr(self, 'action', None) == 'retrieve':
			return [permissions.AllowAny()]
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
		for field in field_list:
			if field in payload:
				setattr(tv, field, payload.get(field))
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
					ip_address=get_client_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
				)
				if file:
					sig.signature_image = file
				else:
					cf, ext = decode_data_url_image(str(data_url))
					if cf:
						sig.signature_image.save(f"installer-signature-technical_visit-{tv.id}.{ext or 'png'}", cf, save=False)
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
					'link_signature': f"/home/installations/{form.id}",
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

	@action(detail=True, methods=['post'], url_path='sign')
	@transaction.atomic
	def sign_document(self, request, pk=None):
		"""Action générique de signature pour différents documents liés à la fiche d'installation.

		Body attendu:
		- document: 'technical_visit' | 'representation_mandate' | ... (à étendre)
		- role: 'client' | 'installer' (optionnel; sinon déduit du rôle utilisateur)
		- signer_name: str
		- signature_file: fichier image (optionnel)
		- signature_data: data URL image (optionnel)
		"""
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

		sig = Signature(
			signer_name=signer_name,
			ip_address=get_client_ip(request),
			user_agent=request.META.get('HTTP_USER_AGENT', ''),
		)
		file = request.FILES.get('signature_file')
		if file:
			sig.signature_image = file
		else:
			data_url = request.data.get('signature_data')
			cf, ext = decode_data_url_image(data_url)
			if cf:
				sig.signature_image.save(f"{role}-signature-{doc}-{form.id}.{ext or 'png'}", cf, save=False)
		sig.save()

		# Affectation selon le type
		if doc == 'technical_visit':
			tv: TechnicalVisit = target
			if role == 'client':
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

			# Génération PDF si complet (après COMMIT pour éviter un état non visible par la page print)
			try:
				if tv.client_signature_id and tv.installer_signature_id:
					def _gen_tv_pdf_after_commit(form_id: str):
						try:
							from .models import Form as _Form
							from .pdf import render_technical_visit_pdf
							f = _Form.objects.select_related('technical_visit').get(pk=form_id)
							pdf_bytes = render_technical_visit_pdf(str(form_id))
							if pdf_bytes and getattr(f, 'technical_visit', None):
								filename = f"technical_visit_{form_id}.pdf"
								try:
									f.technical_visit.report_pdf.save(filename, ContentFile(pdf_bytes), save=True)  # type: ignore
								except Exception:
									pass
						except Exception:
							pass
					transaction.on_commit(lambda fid=str(form.id): _gen_tv_pdf_after_commit(fid))
			except Exception:
				pass

			serializer = TechnicalVisitSerializer(tv, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)

		elif doc == 'representation_mandate':
			rm: RepresentationMandate = target
			if role == 'client':
				if rm.client_signature_id:
					try:
						old = rm.client_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				rm.client_signature = sig
			else:
				if rm.installer_signature_id:
					try:
						old = rm.installer_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				rm.installer_signature = sig

			rm.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])

			# Génération PDF mandat si les deux signatures présentes (après COMMIT)
			try:
				if rm.client_signature_id and rm.installer_signature_id:
					def _gen_rm_pdf_after_commit(form_id: str):
						try:
							from .models import Form as _Form
							from .pdf import render_representation_mandate_pdf
							f = _Form.objects.select_related('representation_mandate').get(pk=form_id)
							pdf_bytes = render_representation_mandate_pdf(str(form_id))
							if pdf_bytes and getattr(f, 'representation_mandate', None):
								filename = f"representation_mandate_{form_id}.pdf"
								try:
									f.representation_mandate.mandate_pdf.save(filename, ContentFile(pdf_bytes), save=True)  # type: ignore
								except Exception:
									pass
						except Exception:
							pass
					transaction.on_commit(lambda fid=str(form.id): _gen_rm_pdf_after_commit(fid))
			except Exception:
				pass

			serializer = RepresentationMandateSerializer(rm, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)

		elif doc == 'enedis_mandate':
			em: EnedisMandate = target
			if role == 'client':
				if em.client_signature_id:
					try:
						old = em.client_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				em.client_signature = sig
			else:
				if em.installer_signature_id:
					try:
						old = em.installer_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				em.installer_signature = sig

			em.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])

			# Génération PDF mandat si les deux signatures présentes (après COMMIT)
			try:
				if em.client_signature_id and em.installer_signature_id:
					def _gen_em_pdf_after_commit(form_id: str):
						try:
							from .models import Form as _Form
							from .pdf import render_enedis_mandate_pdf
							f = _Form.objects.select_related('enedis_mandate').get(pk=form_id)
							pdf_bytes = render_enedis_mandate_pdf(str(form_id))
							if pdf_bytes and getattr(f, 'enedis_mandate', None):
								filename = f"enedis_mandate_{form_id}.pdf"
								try:
									f.enedis_mandate.pdf.save(filename, ContentFile(pdf_bytes), save=True)  # type: ignore
								except Exception:
									pass
						except Exception:
							pass
					transaction.on_commit(lambda fid=str(form.id): _gen_em_pdf_after_commit(fid))
			except Exception:
				pass

			serializer = EnedisMandateSerializer(em, context=self.get_serializer_context())
			return Response(serializer.data, status=status.HTTP_200_OK)
		
		elif doc == 'installation_completed':
			ic: InstallationCompleted = target
			if role == 'client':
				if ic.client_signature_id:
					try:
						old = ic.client_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				ic.client_signature = sig
			else:
				if ic.installer_signature_id:
					try:
						old = ic.installer_signature
						if old and old.signature_image:
							old.signature_image.delete(save=False)
					except Exception:
						pass
				ic.installer_signature = sig

			ic.save(update_fields=['client_signature', 'installer_signature', 'updated_at'])

			# Génération PDF mandat si les deux signatures présentes (après COMMIT)
			try:
				if ic.client_signature_id and ic.installer_signature_id:
					def _gen_ic_pdf_after_commit(form_id: str):
						try:
							from .models import Form as _Form
							from .pdf import render_installation_completed_pdf
							f = _Form.objects.select_related('installation_completed').get(pk=form_id)
							pdf_bytes = render_installation_completed_pdf(str(form_id))
							if pdf_bytes and getattr(f, 'installation_completed', None):
								filename = f"installation_completed_{form_id}.pdf"
								try:
									f.installation_completed.report_pdf.save(filename, ContentFile(pdf_bytes), save=True)  # type: ignore
								except Exception:
									pass
						except Exception:
							pass
					transaction.on_commit(lambda fid=str(form.id): _gen_ic_pdf_after_commit(fid))
			except Exception:
				pass

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
		for field in field_list:
			if field in payload:
				setattr(rm, field, payload.get(field))
		# Éventuelle signature installateur à la création
		if is_create:
			ins_name = (payload.get('installer_signer_name') or '').strip()
			file = request.FILES.get('installer_signature_file')
			data_url = payload.get('installer_signature_data')
			if ins_name and (file or data_url):
				sig = Signature(
					signer_name=ins_name,
					ip_address=get_client_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
				)
				if file:
					sig.signature_image = file
				else:
					cf, ext = decode_data_url_image(str(data_url))
					if cf:
						sig.signature_image.save(f"installer-signature-representation_mandate-{rm.id}.{ext or 'png'}", cf, save=False)
				sig.save()
				rm.installer_signature = sig
		# Validation et sauvegarde
		rm.full_clean()
		rm.save()
		form.status = 'representation_mandate'
		form.save()
		# Email d'information au client (best-effort, non bloquant)
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'representation_mandate': rm,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_signature': f"/home/installations/{form.id}",
				}
				subject = "Mandat de représentation créé – Signature requise"
				send_mail(
					template='emails/installation/representation_mandate_signature_pending.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

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
		field_list = ['client_type', 'client_civility', 'client_address', 'client_company_name', 'client_company_siret', 'client_company_represented_by',
			'contractor_company_name', 'contractor_company_siret', 'contractor_represented_by_name', 'contractor_represented_by_role', 'mandate_type',
			'authorize_signature', 'authorize_payment', 'authorize_l342', 'authorize_network_access', 'geographic_area', 'connection_nature'
		]
		for field in field_list:
			if field in payload:
				setattr(em, field, payload.get(field))
		# Éventuelle signature installateur à la création
		if is_create:
			ins_name = (payload.get('installer_signer_name') or '').strip()
			file = request.FILES.get('installer_signature_file')
			data_url = payload.get('installer_signature_data')
			if ins_name and (file or data_url):
				sig = Signature(
					signer_name=ins_name,
					ip_address=get_client_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
				)
				if file:
					sig.signature_image = file
				else:
					cf, ext = decode_data_url_image(str(data_url))
					if cf:
						# {role}-signature-{doc}-{target.id}
						sig.signature_image.save(f"installer-signature-enedis_mandate-{em.id}.{ext or 'png'}", cf, save=False)
				sig.save()
				em.installer_signature = sig
		# Validation et sauvegarde
		em.full_clean()
		em.save()
		# Email d'information au client (best-effort, non bloquant)
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'enedis_mandate': em,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_signature': f"/home/installations/{form.id}",
				}
				subject = "Mandat Enedis créé – Signature requise"
				send_mail(
					template='emails/installation/enedis_mandate_signature_pending.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

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
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_installation': f"/home/installations/{form.id}",
				}
				subject = "Démarches administratives validées"
				send_mail(
					template='emails/installation/administrative_validated.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

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
		for field in field_list:
			if field in payload:
				setattr(ic, field, payload.get(field))
		for file in file_list:
			if file in request.FILES:
				setattr(ic, file, request.FILES[file])
		# Éventuelle signature installateur à la création
		if is_create:
			ins_name = (payload.get('installer_signer_name') or '').strip()
			file = request.FILES.get('installer_signature_file')
			data_url = payload.get('installer_signature_data')
			if ins_name and (file or data_url):
				sig = Signature(
					signer_name=ins_name,
					ip_address=get_client_ip(request),
					user_agent=request.META.get('HTTP_USER_AGENT', ''),
				)
				if file:
					sig.signature_image = file
				else:
					cf, ext = decode_data_url_image(str(data_url))
					if cf:
						# {role}-signature-{doc}-{target.id}
						sig.signature_image.save(f"installer-signature-installation_completed-{ic.id}.{ext or 'png'}", cf, save=False)
				sig.save()
				ic.installer_signature = sig
		# Validation et sauvegarde
		ic.full_clean()
		ic.save()
		form.status = 'installation_completed'
		form.save()
		# Email d'information au client (best-effort, non bloquant)
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'installation_completed': ic,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_signature': f"/home/installations/{form.id}",
				}
				subject = "Installation terminée – Signature requise"
				send_mail(
					template='emails/installation/installation_completed_signature_pending.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

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
			try:
				client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
				if client_email:
					ctx = {
						'form': form,
						'client_name': f"{form.client_first_name} {form.client_last_name}",
						'link_installation': f"/home/installations/{form.id}",
					}
					subject = "Conformité CONSUEL enregistrée"
					send_mail(
						template='emails/installation/consuel_visit.html',
						context=ctx,
						subject=subject,
						to=client_email,
					)
			except Exception:
				pass

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
		try:
			client_email = getattr(form, 'client', None).email if getattr(form, 'client', None) else form.offer.email
			if client_email:
				ctx = {
					'form': form,
					'client_name': f"{form.client_first_name} {form.client_last_name}",
					'link_installation': f"/home/installations/{form.id}",
				}
				subject = "Raccordement ENEDIS validé"
				send_mail(
					template='emails/installation/enedis_connection_validated.html',
					context=ctx,
					subject=subject,
					to=client_email,
				)
		except Exception:
			pass

		serializer = EnedisConnectionSerializer(ec, context=self.get_serializer_context())
		return Response(serializer.data, status=status.HTTP_201_CREATED if is_create else status.HTTP_200_OK)
	