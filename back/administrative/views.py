from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings

from .models import Cerfa16702
from .serializers import Cerfa16702Serializer
from .pdf import render_cerfa16702_pdf
from installations.models import Form, Signature


class Cerfa16702ViewSet(ModelViewSet):
    queryset = Cerfa16702.objects.all()
    serializer_class = Cerfa16702Serializer

    @action(detail=False, methods=['post'], url_path='forms/(?P<form_id>[^/.]+)/cerfa16702')
    def create_cerfa16702(self, request, form_id=None):
        """Créer ou mettre à jour un CERFA 16702 avec signature."""
        try:
            form = Form.objects.get(pk=form_id)
        except Form.DoesNotExist:
            return Response({'detail': 'Fiche d\'installation non trouvée.'}, status=status.HTTP_404_NOT_FOUND)

        # Récupérer ou créer l'instance CERFA 16702
        cerfa, created = Cerfa16702.objects.get_or_create(
            form=form,
            defaults={'created_by': request.user}
        )

        # Mettre à jour les champs
        cerfa.declarant_type = request.data.get('declarant_type', '')
        cerfa.last_name = request.data.get('last_name', '')
        cerfa.first_name = request.data.get('first_name', '')
        cerfa.birth_date = request.data.get('birth_date', '')
        cerfa.birth_place = request.data.get('birth_place', '')
        cerfa.birth_department = request.data.get('birth_department', '')
        cerfa.birth_country = request.data.get('birth_country', '')
        cerfa.company_denomination = request.data.get('company_denomination', '')
        cerfa.company_reason = request.data.get('company_reason', '')
        cerfa.company_siret = request.data.get('company_siret', '')
        
        cerfa.address_street = request.data.get('address_street', '')
        cerfa.address_number = request.data.get('address_number', '')
        cerfa.address_lieu_dit = request.data.get('address_lieu_dit', '')
        cerfa.address_locality = request.data.get('address_locality', '')
        cerfa.address_postal_code = request.data.get('address_postal_code', '')
        cerfa.address_bp = request.data.get('address_bp', '')
        cerfa.address_cedex = request.data.get('address_cedex', '')
        cerfa.phone_country_code = request.data.get('phone_country_code', '')
        cerfa.phone = request.data.get('phone', '')
        cerfa.email = request.data.get('email', '')
        cerfa.email_consent = request.data.get('email_consent', False)
        
        cerfa.land_street = request.data.get('land_street', '')
        cerfa.land_number = request.data.get('land_number', '')
        cerfa.land_lieu_dit = request.data.get('land_lieu_dit', '')
        cerfa.land_locality = request.data.get('land_locality', '')
        cerfa.land_postal_code = request.data.get('land_postal_code', '')
        cerfa.cadastral_prefix = request.data.get('cadastral_prefix', '')
        cerfa.cadastral_section = request.data.get('cadastral_section', '')
        cerfa.cadastral_number = request.data.get('cadastral_number', '')
        cerfa.cadastral_surface_m2 = request.data.get('cadastral_surface_m2')
        
        cerfa.project_new_construction = request.data.get('project_new_construction', False)
        cerfa.project_existing_works = request.data.get('project_existing_works', False)
        cerfa.project_description = request.data.get('project_description', '')
        cerfa.destination_primary_residence = request.data.get('destination_primary_residence', False)
        cerfa.destination_secondary_residence = request.data.get('destination_secondary_residence', False)
        cerfa.agrivoltaic_project = request.data.get('agrivoltaic_project', False)
        cerfa.electrical_power_text = request.data.get('electrical_power_text', '')
        cerfa.peak_power_text = request.data.get('peak_power_text', '')
        cerfa.energy_destination = request.data.get('energy_destination', '')
        
        cerfa.protection_site_patrimonial = request.data.get('protection_site_patrimonial', False)
        cerfa.protection_site_classe_or_instance = request.data.get('protection_site_classe_or_instance', False)
        cerfa.protection_monument_abords = request.data.get('protection_monument_abords', False)
        
        cerfa.engagement_city = request.data.get('engagement_city', '')
        cerfa.engagement_date = request.data.get('engagement_date', '')
        cerfa.dpc11_notice_materiaux = request.data.get('dpc11_notice_materiaux', '')

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
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
            
            # Gérer le fichier de signature ou la data URL
            signature_file = request.FILES.get('declarant_signature_file')
            if signature_file:
                sig.signature_image = signature_file
            else:
                signature_data = request.data.get('declarant_signature_data')
                if signature_data and signature_data.startswith('data:image/'):
                    cf, ext = self._decode_data_url_image(signature_data)
                    if cf:
                        sig.signature_image.save(f"declarant-signature-cerfa16702-{cerfa.id}.{ext or 'png'}", cf, save=False)
            
            sig.save()
            cerfa.declarant_signature = sig

        cerfa.save()

        # Génération PDF après COMMIT
        try:
            def _gen_cerfa_pdf_after_commit(form_id: str):
                try:
                    from .models import Cerfa16702 as _Cerfa16702
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

    def _get_client_ip(self, request):
        """Récupérer l'IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _decode_data_url_image(self, data_url):
        """Décoder une data URL d'image en ContentFile."""
        if not data_url or not data_url.startswith('data:image/'):
            return None, None
        
        try:
            import base64
            header, data = data_url.split(',', 1)
            ext = header.split(';')[0].split('/')[1]
            if ext == 'jpeg':
                ext = 'jpg'
            
            # Décoder les données base64
            image_data = base64.b64decode(data)
            from django.core.files.base import ContentFile
            return ContentFile(image_data), ext
        except Exception:
            return None, None
