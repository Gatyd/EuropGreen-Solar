import io
import os
from typing import Any, Dict, List

from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from authentication.permissions import HasAdministrativeAccess
from .consuel_serializers import SC144APreviewSerializer

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from EuropGreenSolar.utils.helpers import decode_data_url_image

try:
	from pdfrw import PdfReader, PdfWriter, PageMerge
except Exception:
	PdfReader = None  # type: ignore


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


def preview_sc144a_pdf(request):
	"""Génère un PDF SC-144A en mémoire depuis un payload JSON (aperçu)."""
	try:
		serializer = SC144APreviewSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		items = serializer.get_items()
		y_offset_mm = serializer.validated_data.get("y_offset_mm", 8.0)

		# charger le template
		template_pdf = os.path.join(settings.BASE_DIR, "static", "pdf", "SC-144A.pdf")
		if PdfReader is None:
			return Response({"status": "error", "message": "pdfrw non disponible"}, status=500)
		reader = PdfReader(template_pdf)
		writer = PdfWriter()

		# par page, rendre overlay et fusionner
		for i, pg in enumerate(reader.pages, 1):
			m = pg.MediaBox
			width = float(m[2]) - float(m[0])
			height = float(m[3]) - float(m[1])
			page_items = [it for it in items if int(it.get("page", 1)) == i]
			if not page_items:
				writer.addpage(pg)
				continue
			overlay = _draw_overlay(width, height, page_items, y_offset_mm)
			try:
				ov_reader = PdfReader(overlay)
				ov_pages = getattr(ov_reader, "pages", []) or []
				if len(ov_pages) == 0:
					# Rien à fusionner (overlay vide)
					writer.addpage(pg)
					continue
				overlay_page = ov_pages[0]
				PageMerge(pg).add(overlay_page).render()
				writer.addpage(pg)
			except Exception:
				# En cas de parse d'overlay échoué, on garde la page telle quelle
				writer.addpage(pg)

		out_buf = io.BytesIO()
		writer.write(out_buf)
		out_buf.seek(0)
		resp = HttpResponse(out_buf.getvalue(), content_type="application/pdf")
		resp["Content-Disposition"] = "inline; filename=SC-144A_preview.pdf"
		return resp
	except Exception as e:
		return Response({"status": "error", "message": str(e)}, status=500)


def _normalize_model(value: str | None) -> str | None:
	if not value:
		return None
	v = value.strip().upper().replace(" ", "").replace("_", "-")
	v = v.replace("SC", "SC-") if not v.startswith("SC-") else v
	# accepter variantes: 144A, SC144A, SC-144A
	if v in {"144A", "SC144A", "SC-144A"}:
		return "SC-144A"
	if v in {"144B", "SC144B", "SC-144B"}:
		return "SC-144B"
	if v in {"144C", "SC144C", "SC-144C"}:
		return "SC-144C"
	if v in {"144C2", "SC144C2", "SC-144C2"}:
		return "SC-144C2"
	return value


class ConsuelPreviewAPIView(GenericAPIView):
	permission_classes = [HasAdministrativeAccess]
	serializer_class = SC144APreviewSerializer  # par défaut: SC-144A

	@extend_schema(
		parameters=[
			OpenApiParameter(name="model", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Modèle: SC-144A | SC-144B | SC-144C | SC-144C2 (actuellement seul SC-144A est supporté)")
		],
		request=SC144APreviewSerializer,
		responses={200: {"content": {"application/pdf": {}}}},
		description="Aperçu PDF Consuel. Corps: champs dynamiques selon le modèle; ajouter y_offset_mm si nécessaire."
	)
	def post(self, request, *args, **kwargs):
		try:
			model = _normalize_model(request.query_params.get("model") or request.data.get("model")) or "SC-144A"
			if model != "SC-144A":
				return Response({"status": "error", "message": f"Modèle '{model}' non supporté pour le moment"}, status=400)

			payload = request.data.copy()
			payload.pop("model", None)

			# Tenter de prendre en charge les signatures dessinées transmises en data URL (champ *_data_url)
			# On inspecte la config via un serializer temporaire pour récupérer les clés images.
			temp_serializer = self.get_serializer(data=payload)
			image_keys: List[str] = []
			try:
				for it in getattr(temp_serializer, "_config", []):
					if it.get("type") == "image":
						k = str(it.get("key"))
						if k:
							image_keys.append(k)
			except Exception:
				pass
			# Construire un dict mutable pour insérer des fichiers décodés
			mutable_payload: Dict[str, Any] = {}
			for key in payload:
				mutable_payload[key] = payload.get(key)
			# Pour chaque clé image, si <key> n'est pas fourni en fichier mais <key>_data_url est présent, le décoder
			for k in image_keys:
				data_url_key = f"{k}_data_url"
				if data_url_key in payload and (not payload.get(k)):
					content, ext = decode_data_url_image(payload.get(data_url_key))
					if content:
						# Donner un nom de fichier pour que ImageField soit content
						content.name = f"{k}.{ext or 'png'}"
						mutable_payload[k] = content

			serializer = self.get_serializer(data=mutable_payload)
			serializer.is_valid(raise_exception=True)
			items = serializer.get_items()
			y_offset_mm = serializer.validated_data.get("y_offset_mm", 8.0)

			template_pdf = os.path.join(settings.BASE_DIR, "static", "pdf", "SC-144A.pdf")
			if PdfReader is None:
				print("pdfrw non disponible")
				return Response({"status": "error", "message": "pdfrw non disponible"}, status=500)
			reader = PdfReader(template_pdf)
			writer = PdfWriter()
			for i, pg in enumerate(reader.pages, 1):
				m = pg.MediaBox
				width = float(m[2]) - float(m[0])
				height = float(m[3]) - float(m[1])
				page_items = [it for it in items if int(it.get("page", 1)) == i]
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
			resp = HttpResponse(out_buf.getvalue(), content_type="application/pdf")
			resp["Content-Disposition"] = "inline; filename=consuel_preview.pdf"
			return resp
		except Exception as e:
			print(e)
			return Response({"status": "error", "message": str(e)}, status=500)

