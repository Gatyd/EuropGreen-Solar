from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db import transaction
from django.core.files.base import ContentFile
from EuropGreenSolar.utils.helpers import get_client_ip, decode_data_url_image
from authentication.permissions import HasAdministrativeAccess
from .models import Cerfa16702, ElectricalDiagram
from installations.models import AdministrativeValidation
from .serializers import Cerfa16702Serializer, ElectricalDiagramSerializer
from installations.models import Form, Signature
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from EuropGreenSolar.utils.pdf import extract_pdf_fields, fill_pdf, CERFA_FIELD_MAPPING
from datetime import datetime

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

@api_view(["GET"])
@permission_classes([AllowAny])  # publique pour ton test
def get_cerfa_fields(request):
    """
    Retourne tous les champs du Cerfa officiel au format JSON
    """
    pdf_path = os.path.join(settings.BASE_DIR, "static/pdf/cerfa_16702.pdf")
    try:
        fields = extract_pdf_fields(pdf_path)
        return Response({"status": "success", "fields": fields})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
    
@api_view(["POST"])
@permission_classes([AllowAny])  # à sécuriser plus tard !
def generate_cerfa_pdf(request):
    """
    Remplit le PDF Cerfa16702 avec les données d'un enregistrement existant.
    """
    # cerfa_id = request.data.get("cerfa_id")
    # if not cerfa_id:
    #     return Response({"status": "error", "message": "cerfa_id manquant"}, status=400)

    try:
        cerfa = Cerfa16702.objects.get(form_id='6a9b1e52-05dd-402d-a31c-bba5a890cd67')
    except Cerfa16702.DoesNotExist:
        return Response({"status": "error", "message": "Cerfa introuvable"}, status=404)

    # Construire le dict pour remplir le PDF
    data = {}
    for field, pdf_field in CERFA_FIELD_MAPPING.items():
        value = getattr(cerfa, field, "")
        if value is None:
            value = ""
        # Cas 1 : dates
        if "date" in field:
            value = format_date(value)

        # Cas 2 : email (split en deux champs)
        if field == "email":
            user, domain = split_email(value)
            data["D5GE1_email"] = user
            data["D5GE2_email"] = domain
            continue  # on ne mappe pas directement "email"

        # Cas 3 : signature (forcer affichage du nom)
        if field == "signer_name":
            if not value and hasattr(cerfa, "declarant_signature") and cerfa.declarant_signature:
                value = cerfa.declarant_signature.signer_name
        data[pdf_field] = str(value)

    # Générer le PDF
    input_pdf = os.path.join(settings.BASE_DIR, "static/pdf/cerfa_16702.pdf")
    output_dir = os.path.join(settings.MEDIA_ROOT, "cerfa_pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_pdf = os.path.join(output_dir, f"cerfa_16702_{cerfa.id}.pdf")

    fill_pdf(input_pdf, output_pdf, data)

    # Construire l'URL publique
    pdf_url = request.build_absolute_uri(
        os.path.join(settings.MEDIA_URL, "cerfa_pdfs", f"cerfa_16702_{cerfa.id}.pdf")
    )

    return Response({
        "status": "success",
        "pdf_url": pdf_url
    })

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

        # Gérer la signature du déclarant
        declarant_signer_name = request.data.get('declarant_signer_name', '').strip()
        if declarant_signer_name:
            # Supprimer l'ancienne signature si elle existe
            if cerfa.declarant_signature_id:
                try:
                    old_sig = cerfa.declarant_signature
                    if old_sig and old_sig.signature_image:
                        old_sig.signature_image.delete(save=False)
                    old_sig.delete()
                except Exception:
                    pass

            # Créer la nouvelle signature
            sig = Signature(
                signer_name=declarant_signer_name,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Gérer le fichier de signature ou la data URL
            signature_file = request.FILES.get('declarant_signature_file')
            if signature_file:
                sig.signature_image = signature_file
            else:
                signature_data = request.data.get('declarant_signature_data')
                if signature_data and signature_data.startswith('data:image/'):
                    cf, ext = decode_data_url_image(signature_data)
                    if cf:
                        sig.signature_image.save(f"declarant-signature-cerfa16702-{cerfa.id}.{ext or 'png'}", cf, save=False)
            
            sig.save()
            cerfa.declarant_signature = sig

        cerfa.save()

        # Génération PDF après COMMIT
        try:
            def _gen_cerfa_pdf_after_commit(form_id: str):
                try:
                    from .pdf import render_cerfa16702_pdf
                    f = Form.objects.select_related('cerfa16702').get(pk=form_id)
                    pdf_bytes = render_cerfa16702_pdf(str(form_id))
                    if pdf_bytes and getattr(f, 'cerfa16702', None):
                        filename = f"cerfa16702_{form_id}.pdf"
                        try:
                            f.cerfa16702.pdf.save(filename, ContentFile(pdf_bytes), save=True)
                        except Exception:
                            pass
                except Exception:
                    pass
            
            transaction.on_commit(lambda fid=str(form.id): _gen_cerfa_pdf_after_commit(fid))
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