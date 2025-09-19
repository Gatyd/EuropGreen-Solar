import io
import os
from typing import Any, Dict, List

from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.core.files.base import ContentFile
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from authentication.permissions import HasAdministrativeAccess
from .consuel_serializers import (
	SC144APreviewSerializer,
	SC144BPreviewSerializer,
	SC144CPreviewSerializer,
	SC144C2PreviewSerializer,
	ConsuelPreviewSerializer,
)
from .models import Consuel
from installations.models import AdministrativeValidation, Form, Signature

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from EuropGreenSolar.utils.helpers import decode_data_url_image

try:
	from pdfrw import PdfReader, PdfWriter, PageMerge
except Exception:
	PdfReader = None  # type: ignore
	PdfWriter = None  # type: ignore
	PageMerge = None  # type: ignore


def _draw_overlay(width: float, height: float, items: List[Dict[str, Any]], y_offset_mm: float):
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=(width, height))
	for it in items:
		# Positions définies en mm dans la config; appliquer un décalage vertical si fourni
		x = float(it["x"]) * mm
		y_mm = float(it["y"]) # - float(y_offset_mm or 0)
		y = height - y_mm * mm  # origine haut-gauche -> bas-gauche
		t = it.get("type")
		val = it.get("value")
		if t == "text":
			# Afficher uniquement si une valeur utilisateur est fournie
			if val not in (None, ""):
				c.setFont("Helvetica", 9)
				c.drawString(x, y, str(val))
		elif t == "checkbox":
			# Dessiner uniquement la croix si True; ne pas dessiner de case (présente sur le template)
			if val:
				size = 2 * mm
				x0, y0 = x - size/2, y - size/2
				c.line(x0, y0, x0+size, y0+size)
				c.line(x0, y0+size, x0+size, y0)
		elif t == "radio":
			# Bouton radio: rond plein si True
			if val:
				radius_mm = float(it.get("r", 1.5))
				r = radius_mm * mm
				c.circle(x, y, r, stroke=0, fill=1)
		elif t == "image":
			# N'afficher l'image que si fournie; pas de placeholder pour l'aperçu
			if val:
				try:
					image_obj = None
					# val peut être un fichier Django (InMemoryUploadedFile, ContentFile) ou un chemin/bytes
					# Support minimal: UploadedFile/ContentFile/bytes/chemin
					if hasattr(val, "read"):
						# Remettre le curseur en début au cas où
						try:
							val.seek(0)
						except Exception:
							pass
						image_obj = ImageReader(val)
					elif isinstance(val, (bytes, bytearray)):
						image_obj = ImageReader(io.BytesIO(val))
					elif isinstance(val, str):
						# On peut accepter une data URL brute si passée jusqu'ici (peu probable après validation)
						if val.startswith("data:image/"):
							content, _ext = decode_data_url_image(val)
							if content:
								try:
									content.seek(0)
								except Exception:
									pass
								image_obj = ImageReader(content)
						else:
							# considérer comme chemin de fichier
							if os.path.exists(val):
								image_obj = ImageReader(val)

					if image_obj is not None:
						# Dimensions: utiliser w/h (mm) si fournis; sinon garder ratio à partir de l'image
						target_w_mm = it.get("w")
						target_h_mm = it.get("h")
						if target_w_mm and target_h_mm:
							w_pt = float(target_w_mm) * mm
							h_pt = float(target_h_mm) * mm
						else:
							# Taille par défaut: 30x15 mm si non spécifié, en conservant le ratio
							iw, ih = image_obj.getSize()
							default_w_pt = 30.0 * mm
							if iw and ih:
								ratio = ih / float(iw)
								w_pt = float(target_w_mm) * mm if target_w_mm else default_w_pt
								h_pt = float(target_h_mm) * mm if target_h_mm else (w_pt * ratio)
							else:
								w_pt = default_w_pt
								h_pt = 15.0 * mm

						# drawImage attend le coin inférieur-gauche; notre y est calé sur la ligne de base/haut
						c.drawImage(image_obj, x, y - h_pt, width=w_pt, height=h_pt, preserveAspectRatio=True, mask='auto')
				except Exception:
					pass
	c.save()
	buf.seek(0)
	return buf


def _filter_items_for_page(items: List[Dict[str, Any]], page_index: int, page_height_pts: float) -> List[Dict[str, Any]]:
	"""
	Supporte deux modes de positionnement:
	- Position locale par page: l'item a un champ 'page' (1-based) et 'y' exprimé en mm pour cette page.
	- Position globale continue: l'item n'a pas de champ 'page' et 'y' est exprimé en mm depuis le haut de la première page;
	  on en déduit la page via la hauteur de page et on convertit en y local pour cette page.

	Retourne uniquement les items appartenant à la page demandée, avec 'y' normalisé en mm locaux.
	"""
	out: List[Dict[str, Any]] = []
	try:
		page_height_mm = float(page_height_pts) / float(mm) if page_height_pts else 0.0
	except Exception:
		page_height_mm = 0.0
	for it in items:
		try:
			raw_y = float(it.get("y", 0))
			has_page_flag = it.get("page") is not None
			p_flag = int(it.get("page", 1)) if has_page_flag else None

			if has_page_flag:
				# Si la config a injecté page=1 par défaut mais y dépasse la hauteur -> interpréter comme global
				if page_height_mm > 0 and raw_y >= page_height_mm:
					# recalcul global
					p = int(raw_y // page_height_mm) + 1
					if p != page_index:
						continue
					y_local = raw_y - (p - 1) * page_height_mm
				else:
					# Mode local classique
					if p_flag != page_index:
						continue
					y_local = raw_y
			else:
				# Mode global sans page explicite
				if page_height_mm > 0:
					p = int(raw_y // page_height_mm) + 1
					if p != page_index:
						continue
					y_local = raw_y - (p - 1) * page_height_mm
				else:
					if page_index != 1:
						continue
					y_local = raw_y

			new_it = dict(it)
			new_it["y"] = y_local
			out.append(new_it)
		except Exception:
			continue
	return out


def _fmt_date_ddmmyyyy(value: str | None) -> str:
	"""YYYY-MM-DD -> DD/MM/YYYY; passthrough otherwise."""
	if not value:
		return ""
	try:
		from datetime import datetime as _dt
		return _dt.strptime(str(value), "%Y-%m-%d").strftime("%d/%m/%Y")
	except Exception:
		return str(value)


def _prepare_payload_for_pdf(raw_payload: Dict[str, Any], template: str = "144a") -> Dict[str, Any]:
	"""Clone and normalize payload for PDF generation:
	- decode any <image_key>_data_url to a ContentFile and assign to key
	- accept direct files from request.FILES (caller should inject them)
	- format dates (reference_date to dd/mm/yyyy; ensure signature_date present -> today)
	"""
	# Shallow copy
	payload: Dict[str, Any] = {}
	for k in raw_payload:
		payload[k] = raw_payload.get(k)

	# Discover image keys from serializer config for this template
	try:
		_temp = ConsuelPreviewSerializer(data={}, template=template)
		image_keys: List[str] = [str(it.get("key")) for it in getattr(_temp, "_config", []) if it.get("type") == "image" and it.get("key")]
	except Exception:
		image_keys = []

	# Decode data URLs when file not present
	for k in image_keys:
		du_key = f"{k}_data_url"
		if du_key in raw_payload and (not raw_payload.get(k)):
			content, ext = decode_data_url_image(raw_payload.get(du_key))
			if content:
				content.name = f"{k}.{ext or 'png'}"
				payload[k] = content

	# Dates normalization
	if payload.get("reference_date"):
		payload["reference_date"] = _fmt_date_ddmmyyyy(payload.get("reference_date"))
	# signature_date default to today if not provided
	from datetime import datetime as _dt
	if not payload.get("signature_date"):
		payload["signature_date"] = _dt.now().strftime("%d/%m/%Y")

	return payload


def generate_consuel_pdf(raw_payload: Dict[str, Any], template: str = "144a") -> bytes:
	"""Generate Consuel PDF bytes for given template using overlay logic.

	Currently supported: '144a' (maps to static/pdf/SC-144A.pdf).
	Raises ValueError for unsupported templates or when pdfrw not available.
	"""
	template = (template or "").strip().lower() or "144a"
	if template not in {"144a", "144b", "144c", "144c2"}:
		raise ValueError("template invalide")

	if PdfReader is None or PdfWriter is None or PageMerge is None:
		raise RuntimeError("pdfrw non disponible")

	# Normalize payload
	payload = _prepare_payload_for_pdf(raw_payload, template=template)

	# Build items via serializer (chooser per template)
	tpl = template
	if tpl == "144a":
		ser = SC144APreviewSerializer(data=payload)
	elif tpl == "144b":
		ser = SC144BPreviewSerializer(data=payload)
	elif tpl == "144c":
		ser = SC144CPreviewSerializer(data=payload)
	else:  # 144c2
		ser = SC144C2PreviewSerializer(data=payload)
	ser.is_valid(raise_exception=True)
	items = ser.get_items()
	y_offset_mm = ser.validated_data.get("y_offset_mm", 8.0)

	# Template file mapping
	input_file_name = f"SC-144{'A' if template == '144a' else 'B' if template == '144b' else 'C' if template == '144c' else 'C2'}.pdf"
	input_pdf = os.path.join(settings.BASE_DIR, "static", "pdf", input_file_name)
	reader = PdfReader(input_pdf)
	writer = PdfWriter()
	for i, pg in enumerate(reader.pages, 1):
		m = pg.MediaBox
		width = float(m[2]) - float(m[0])
		height = float(m[3]) - float(m[1])
		# Support des coordonnées globales (y au-delà d'une page) et des items sans 'page'
		page_items = _filter_items_for_page(items, i, height)
		if not page_items:
			writer.addpage(pg)
			continue
		overlay = _draw_overlay(width, height, page_items, y_offset_mm)
		try:
			ov_reader = PdfReader(overlay)
			ov_pages = getattr(ov_reader, "pages", []) or []
			if len(ov_pages) == 0:
				writer.addpage(pg)
				continue
			overlay_page = ov_pages[0]
			PageMerge(pg).add(overlay_page).render()
			writer.addpage(pg)
		except Exception:
			writer.addpage(pg)

	out_buf = io.BytesIO()
	writer.write(out_buf)
	out_buf.seek(0)
	return out_buf.getvalue()


def _normalize_template(value: str | None) -> str:
	"""Normalize template to one of: 144a, 144b, 144c, 144c2. Defaults to 144a."""
	if not value:
		return "144a"
	v = value.strip().lower()
	if v in {"144a", "144b", "144c", "144c2"}:
		return v
	# try to coerce common variants
	v2 = v.replace("sc-", "").replace("sc", "").replace(" ", "")
	if v2 in {"144a", "144b", "144c", "144c2"}:
		return v2
	return "144a"


class ConsuelPreviewAPIView(GenericAPIView):
	permission_classes = [HasAdministrativeAccess]

	@extend_schema(
		parameters=[
			OpenApiParameter(name="template", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Template: 144a | 144b | 144c | 144c2 (actuellement seul 144a est supporté)")
		],
		request=SC144APreviewSerializer,
		responses={200: {"content": {"application/pdf": {}}}},
		description="Aperçu PDF Consuel. Corps: champs dynamiques selon le template; ajouter y_offset_mm si nécessaire."
	)
	def post(self, request, *args, **kwargs):
		try:
			tpl = _normalize_template(request.query_params.get("template") or request.data.get("template"))
			pdf_bytes = generate_consuel_pdf(request.data, template=tpl)
			resp = HttpResponse(pdf_bytes, content_type="application/pdf")
			resp["Content-Disposition"] = "inline; filename=consuel_preview.pdf"
			return resp
		except ValueError as e:
			return Response({"status": "error", "message": str(e)}, status=400)
		except Exception as e:
			print(e)
			return Response({"status": "error", "message": str(e)}, status=500)


class ConsuelViewSet(GenericViewSet):
	queryset = Consuel.objects.all()
	serializer_class = None  # serializer not needed for actions here; use ConsuelSerializer via import when responding
	permission_classes = [HasAdministrativeAccess]

	@action(detail=False, methods=['post'], url_path='form/(?P<form_id>[^/.]+)')
	def create_consuel(self, request, form_id=None):
		"""Créer ou mettre à jour un Consuel pour une fiche Installation, avec signature installateur et PDF généré."""
		from .serializers import ConsuelSerializer  # local import to avoid circular
		try:
			form = Form.objects.get(pk=form_id)
		except Form.DoesNotExist:
			return Response({'detail': "Fiche d'installation non trouvée."}, status=status.HTTP_404_NOT_FOUND)

		administrative_validation = getattr(form, 'administrative_validation', None)
		if not administrative_validation:
			AdministrativeValidation.objects.create(form=form, created_by=request.user)

		payload = request.data

		# Template (strict)
		template = _normalize_template(payload.get('template'))

		consuel = Consuel.objects.create(
			form=form,
			template=template,
			created_by=request.user
		)

		# Signature installateur (enregistrer le modèle Signature)
		signer_name = (payload.get('installer_name') or '').strip()
		if consuel.installer_signature_id:
			try:
				old_sig = consuel.installer_signature
				if old_sig and getattr(old_sig, 'signature_image', None):
					old_sig.signature_image.delete(save=False)
				old_sig.delete()
			except Exception:
				pass
		if signer_name:
			sig = Signature(
				signer_name=signer_name,
				ip_address=getattr(request, 'META', {}).get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR', ''),
				user_agent=request.META.get('HTTP_USER_AGENT', ''),
			)
			file_field = request.FILES.get('installer_signature')
			if file_field:
				sig.signature_image = file_field
			else:
				data_url = payload.get('installer_signature_data_url')
				if data_url:
					content, ext = decode_data_url_image(data_url)
					if content:
						content.name = f"installer_signature.{ext or 'png'}"
						sig.signature_image = content
			sig.save()
			consuel.installer_signature = sig

		consuel.save()

		try:
			# Préparer un payload mutable avec fichiers éventuels (tampon)
			mutable_payload: Dict[str, Any] = {k: payload.get(k) for k in payload}
			if 'installer_stamp' not in request.FILES and payload.get('installer_stamp_data_url'):
				content, ext = decode_data_url_image(payload.get('installer_stamp_data_url'))
				if content:
					content.name = f"installer_stamp.{ext or 'png'}"
					mutable_payload['installer_stamp'] = content
			else:
				if 'installer_stamp' in request.FILES:
					mutable_payload['installer_stamp'] = request.FILES['installer_stamp']

			pdf_bytes = generate_consuel_pdf(mutable_payload, template=template)
			filename = f"consuel_{consuel.id}.pdf"
			consuel.pdf.save(filename, ContentFile(pdf_bytes), save=True)
		except Exception:
			pass

		serializer = ConsuelSerializer(consuel, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)

