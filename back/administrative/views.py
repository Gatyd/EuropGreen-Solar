from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.core.files.base import ContentFile
from EuropGreenSolar.utils.helpers import get_client_ip
from EuropGreenSolar.utils.helpers import decode_data_url_image
from authentication.permissions import HasAdministrativeAccess
from .models import Cerfa16702, ElectricalDiagram, Consuel
from installations.models import AdministrativeValidation
from .serializers import Cerfa16702Serializer, ElectricalDiagramSerializer
from .serializers import ConsuelSerializer
from .serializers import EnedisMandatePreviewSerializer
from installations.models import Form, Signature
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from EuropGreenSolar.utils.pdf import fill_pdf_bytes
from datetime import datetime
from django.http import HttpResponse
from .pdf import CERFA_FIELD_MAPPING
from .pdf import render_cerfa16702_attachments_pdf
from .consuel_views import _draw_overlay, _filter_items_for_page
import io
try:
    from pdfrw import PdfReader, PdfWriter, PageMerge
except Exception:
    PdfReader = None  # type: ignore
    PdfWriter = None  # type: ignore
    PageMerge = None  # type: ignore

def format_date(value):
    """Transforme YYYY-MM-DD -> DDMMYYYY"""
    if not value:
        return ""
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").strftime("%d%m%Y")
    except Exception:
        return str(value)  # fallback brut
    
def split_email(email):
    if not email or "@" not in email:
        return "", ""
    user, domain = email.split("@", 1)
    return user, domain


def build_pdf_data_from_payload(payload: dict) -> dict:
    """Construit le dict de champs PDF à partir d'un payload JSON/QueryDict.
    - Formate les dates *YYYY-MM-DD* -> *DDMMYYYY*
    - Split l'email en 2 champs si présent
    - Convertit booléens en "1"/"0" si nécessaire
    - Tolère les valeurs manquantes (chaine vide)
    """
    data: dict[str, str] = {}
    # payload peut être un QueryDict; le caster en dict simple pour .get
    def _get(key, default=""):
        try:
            return payload.get(key, default)
        except Exception:
            return payload[key] if key in payload else default
    
    def _truthy(v) -> bool:
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        return s in {"1", "true", "yes", "on", "oui", "vrai"}

    for field, pdf_field in CERFA_FIELD_MAPPING.items():
        value = _get(field, "")
        # dates
        if "date" in field and value:
            value = format_date(value)
        # booléens envoyés parfois comme True/False ou "1"/"0"
        if isinstance(value, bool):
            value = "1" if value else "0"
        # email: split en 2 champs et continue
        if field == "email":
            user, domain = split_email(value)
            data["D5GE1_email"] = user
            data["D5GE2_email"] = domain
            continue
        if field == 'agrivoltaic_project':
            is_yes = _truthy(value)
            # Oui => C2ZI0 = 1, Non => C2ZI1 = 1
            data["C2ZI0_agrivoltaique"] = "1" if is_yes else "0"
            data["C2ZI1_agrivoltaique"] = "0" if is_yes else "1"
            # Ne pas écrire data[pdf_field] ensuite (évite d'écraser)
            continue
        # signature: le preview ne persiste pas; si signer_name absent, on peut le déduire du nom+prénom
        if field == "signer_name":
            if not value:
                fn = _get("first_name", "").strip()
                ln = _get("last_name", "").strip()
                if fn or ln:
                    value = f"{fn} {ln}".strip()
        data[pdf_field] = "" if value is None else str(value)
    data["D1N_nom"] = _get("last_name", "") if _get("declarant_type", "") == "individual" else ""
    data["D1P_prenom"] = _get("first_name", "") if _get("declarant_type", "") == "individual" else ""
    data["D2N_nom"] = _get("last_name", "") if _get("declarant_type", "") == "company" else ""
    data["D2P_prenom"] = _get("first_name", "") if _get("declarant_type", "") == "company" else ""
    data["P5PA1"] = "1"
    data["P5PB1"] = "1"
    data["P3GE1"] = "1"
    data["P3GD1"] = "1"
    data["P5PC1"] = "1"
    data["P3GF1"] = "1"
    data["P3GG1"] = "1"
    data["P3GH1"] = "1"
    data["P4LC1"] = "1"
    data["P4CD1"] = "1"

    return data

@api_view(["POST"])
@permission_classes([HasAdministrativeAccess])
def preview_cerfa_pdf(request):
    """
    Génère un PDF CERFA 16702 en mémoire depuis un payload JSON (aperçu).
    Ne persiste rien; renvoie application/pdf.
    """
    try:
        payload = request.data
        # Construire data
        data = build_pdf_data_from_payload(payload)
        input_pdf = os.path.join(settings.BASE_DIR, "static/pdf/cerfa_16702.pdf")
        pdf_bytes = fill_pdf_bytes(input_pdf, data)
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = "inline; filename=cerfa16702_preview.pdf"
        return resp
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
    
class Cerfa16702ViewSet(GenericViewSet):
    queryset = Cerfa16702.objects.all()
    serializer_class = Cerfa16702Serializer
    permission_classes = [HasAdministrativeAccess]

    @action(detail=False, methods=['post'], url_path='form/(?P<form_id>[^/.]+)')
    def create_cerfa16702(self, request, form_id=None):
        """Créer ou mettre à jour un CERFA 16702 avec signature."""
        try:
            form = Form.objects.get(pk=form_id)
        except Form.DoesNotExist:
            return Response({'detail': 'Fiche d\'installation non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        # safe check: accessing a reverse one-to-one may raise RelatedObjectDoesNotExist
        administrative_validation = getattr(form, 'administrative_validation', None)
        if not administrative_validation:
            AdministrativeValidation.objects.create(form=form, created_by=request.user)

        payload = request.data
        # Récupérer ou créer l'instance CERFA 16702
        cerfa, created = Cerfa16702.objects.get_or_create(
            form=form,
            defaults={'created_by': request.user}
        )
        field_list = [
            'declarant_type', 'last_name', 'first_name', 'birth_date', 'birth_place', 'birth_department', 'birth_country', 'company_denomination', 'company_reason', 'company_siret',
            'address_street', 'address_number', 'address_lieu_dit', 'address_locality', 'address_postal_code', 'address_bp', 'address_cedex', 'phone_country_code', 'phone', 'email', 'email_consent',
            'land_street', 'land_number', 'land_lieu_dit', 'land_locality', 'land_postal_code', 'cadastral_prefix', 'cadastral_section', 'cadastral_number', 'cadastral_surface_m2',
            'project_new_construction', 'project_existing_works', 'project_description', 'destination_primary_residence', 'destination_secondary_residence', 'agrivoltaic_project',
            'electrical_power_text', 'peak_power_text', 'energy_destination', 'protection_site_patrimonial', 'protection_site_classe_or_instance', 'protection_monument_abords',
            'engagement_city', 'engagement_date', 'dpc11_notice_materiaux'
        ]

        # Mettre à jour les champs
        for field in field_list:
            setattr(cerfa, field, payload.get(field))

        # Gérer les pièces jointes
        for i in range(1, 9):
            field_name = f'dpc{i}'
            if field_name in request.FILES:
                setattr(cerfa, field_name, request.FILES[field_name])
        
        if 'dpc11' in request.FILES:
            cerfa.dpc11 = request.FILES['dpc11']

        # Gérer la signature du déclarant (nom uniquement, dérivé si absent)
        signer_name = (request.data.get('declarant_signer_name') or '').strip()
        if not signer_name:
            fn = (request.data.get('first_name') or '').strip()
            ln = (request.data.get('last_name') or '').strip()
            signer_name = f"{fn} {ln}".strip()
        if signer_name:
            # Supprimer l'ancienne signature si elle existe
            if cerfa.declarant_signature_id:
                try:
                    old_sig = cerfa.declarant_signature
                    if old_sig and getattr(old_sig, 'signature_image', None):
                        old_sig.signature_image.delete(save=False)
                    old_sig.delete()
                except Exception:
                    pass
            sig = Signature(
                signer_name=signer_name,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            sig.save()
            cerfa.declarant_signature = sig

        cerfa.save()

        # Génération PDF après COMMIT (basée sur le PDF statique rempli)
        try:
            def _gen_cerfa_pdf_after_commit(form_id: str):
                try:
                    f = Form.objects.select_related('cerfa16702').get(pk=form_id)
                    c = getattr(f, 'cerfa16702', None)
                    if not c:
                        return
                    cerfa_payload = {fld: getattr(c, fld, "") for fld in CERFA_FIELD_MAPPING.keys()}
                    if getattr(c, 'declarant_signature', None):
                        cerfa_payload['signer_name'] = c.declarant_signature.signer_name
                    data_local = build_pdf_data_from_payload(cerfa_payload)
                    input_pdf = os.path.join(settings.BASE_DIR, "static/pdf/cerfa_16702.pdf")
                    pdf_bytes = fill_pdf_bytes(input_pdf, data_local)
                    if pdf_bytes:
                        filename = f"cerfa16702_{form_id}.pdf"
                        f.cerfa16702.pdf.save(filename, ContentFile(pdf_bytes), save=True)
                except Exception:
                    pass
            
            transaction.on_commit(lambda fid=str(form.id): _gen_cerfa_pdf_after_commit(fid))
        except Exception:
            pass

        serializer = Cerfa16702Serializer(cerfa, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='attachments')
    def update_attachments(self, request, pk=None):
        """Met à jour les pièces jointes DPC1..DPC8, DPC11 d'un CERFA par son id, puis génère le PDF des pièces jointes."""
        try:
            cerfa = Cerfa16702.objects.get(pk=pk)
        except Cerfa16702.DoesNotExist:
            return Response({'detail': 'CERFA introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Mise à jour des fichiers
        for i in range(1, 9):
            field_name = f'dpc{i}'
            if field_name in request.FILES:
                setattr(cerfa, field_name, request.FILES[field_name])
        if 'dpc11' in request.FILES:
            cerfa.dpc11 = request.FILES['dpc11']
        if 'dpc11_notice_materiaux' in request.data:
            cerfa.dpc11_notice_materiaux = request.data.get('dpc11_notice_materiaux') or ''

        cerfa.save()

        # Générer le PDF des pièces jointes via la page print front
        try:
            form_id = str(cerfa.form_id)
            pdf_bytes = render_cerfa16702_attachments_pdf(form_id, request=request)
            if pdf_bytes:
                filename = f"cerfa16702_attachments_{cerfa.id}.pdf"
                cerfa.attachements_pdf.save(filename, ContentFile(pdf_bytes), save=True)
        except Exception:
            pass

        serializer = Cerfa16702Serializer(cerfa, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ElectricalDiagramViewSet(GenericViewSet):
    queryset = ElectricalDiagram.objects.all()
    serializer_class = ElectricalDiagramSerializer
    permission_classes = [HasAdministrativeAccess]

    @action(detail=False, methods=['post'], url_path='form/(?P<form_id>[^/.]+)')
    def create_electrical_diagram(self, request, form_id=None):
        """Créer ou mettre à jour un Schéma électrique."""
        try:
            form = Form.objects.get(pk=form_id)
        except Form.DoesNotExist:
            return Response({'detail': 'Fiche d\'installation non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
        
        administrative_validation = getattr(form, 'administrative_validation', None)
        if not administrative_validation:
            AdministrativeValidation.objects.create(form=form, created_by=request.user)

        electric_diagram, created = ElectricalDiagram.objects.get_or_create(
            form=form,
            defaults={'created_by': request.user}
        )
        
        file = request.FILES['file']
        if not file:
            return Response({'detail': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

        setattr(electric_diagram, 'file', file)
        electric_diagram.save()

        serializer = ElectricalDiagramSerializer(electric_diagram, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


## ConsuelViewSet déplacé dans consuel_views.py


class EnedisMandatePreviewAPIView(GenericAPIView):
    """Aperçu PDF du Mandat ENEDIS (Enedis-FOR-RAC_02E.pdf) via overlay pdfrw.

    Corps tolérant validé par EnedisMandatePreviewSerializer.
    Réponse: application/pdf (inline).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated and user.is_staff:
            permission_classes = [HasAdministrativeAccess]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]

    def post(self, request, *args, **kwargs):
        if PdfReader is None or PdfWriter is None or PageMerge is None:
            return Response({"status": "error", "message": "pdfrw non disponible"}, status=500)

        ser = EnedisMandatePreviewSerializer(data=request.data)
        if not ser.is_valid():
            print(ser.errors)
            return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

        # Construire les items overlay
        items = ser.get_items()
        y_offset_mm = ser.validated_data.get("y_offset_mm", 8.0)

        # Charger le template du mandat ENEDIS
        input_pdf = os.path.join(settings.BASE_DIR, "static", "pdf", "Enedis-FOR-RAC_02E.pdf")
        try:
            reader = PdfReader(input_pdf)
        except Exception as e:
            return Response({"status": "error", "message": f"Template introuvable: {e}"}, status=500)

        writer = PdfWriter()
        for i, pg in enumerate(reader.pages, 1):
            try:
                m = pg.MediaBox
                width = float(m[2]) - float(m[0])
                height = float(m[3]) - float(m[1])
            except Exception:
                # fallback: dimensions lettre si non trouvées
                from reportlab.lib.pagesizes import letter as _letter
                width, height = _letter

            page_items = _filter_items_for_page(items, i, height)
            if not page_items:
                writer.addpage(pg)
                continue

            overlay_buf = _draw_overlay(width, height, page_items, y_offset_mm)
            try:
                ov_reader = PdfReader(overlay_buf)
                ov_pages = getattr(ov_reader, "pages", []) or []
                if len(ov_pages) == 0:
                    writer.addpage(pg)
                    continue
                PageMerge(pg).add(ov_pages[0]).render()
                writer.addpage(pg)
            except Exception:
                writer.addpage(pg)

        out_buf = io.BytesIO()
        writer.write(out_buf)
        out_buf.seek(0)
        resp = HttpResponse(out_buf.read(), content_type="application/pdf")
        resp["Content-Disposition"] = "inline; filename=enedis_mandate_preview.pdf"
        return resp