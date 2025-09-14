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

try:
	from pdfrw import PdfReader, PdfWriter, PageMerge
except Exception:
	PdfReader = None  # type: ignore


def _draw_overlay(width: float, height: float, items: List[Dict[str, Any]], y_offset_mm: float):
	buf = io.BytesIO()
	c = canvas.Canvas(buf, pagesize=(width, height))
	for it in items:
		x = float(it["x"]) * mm
		y = float(it["y"]) #- float(y_offset_mm)
		y = height - y * mm  # origine haut-gauche -> bas-gauche
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
					# À implémenter selon le type (fichier uplodé ou bytes); laissé vide pour l'instant
					pass
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
			serializer = self.get_serializer(data=payload)
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

