from rest_framework import serializers
from .models import Cerfa16702, ElectricalDiagram, EnedisMandate, Consuel
from installations.models import Signature
from typing import Any, Dict, List
from django.utils import timezone

class SignatureSerializer(serializers.ModelSerializer):
	class Meta:
		model = Signature
		fields = [
			'id', 'signer_name', 'ip_address', 'user_agent', 'signed_at', 'signature_image', 'created_at'
		]

class Cerfa16702Serializer(serializers.ModelSerializer):
    declarant_signature = SignatureSerializer(read_only=True)
    class Meta:
        model = Cerfa16702
        fields = '__all__'
        read_only_fields = ('id', 'form', 'created_by', 'created_at', 'updated_at')

class ElectricalDiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricalDiagram
        fields = '__all__'

class EnedisMandateSerializer(serializers.ModelSerializer):
    client_signature = SignatureSerializer(read_only=True)
    installer_signature = SignatureSerializer(read_only=True)
    class Meta:
        model = EnedisMandate
        fields = '__all__'

class ConsuelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Consuel
        fields = '__all__'


class EnedisMandatePreviewSerializer(serializers.Serializer):
    """
    Serializer d'aperçu souple (tous champs optionnels) pour générer un overlay PDF.
    Ne valide pas les contraintes métier strictes; vise la tolérance pour un preview.
    """
    # Parties prenantes — Client
    client_type = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.ClientType.choices], required=False, allow_null=True, allow_blank=True)
    client_civility = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.Civility.choices], required=False, allow_null=True, allow_blank=True)
    client_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    client_company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_company_siret = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_company_represented_by_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_company_represented_by_role = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    contractor_type = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.ClientType.choices], required=False, allow_null=True, allow_blank=True)
    contractor_civility = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.Civility.choices], required=False, allow_null=True, allow_blank=True)
    contractor_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contractor_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contractor_company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contractor_company_siret = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contractor_company_represented_by_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contractor_company_represented_by_role = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    mandate_type = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.MandateType.choices], required=False, allow_null=True, allow_blank=True)

    authorize_signature = serializers.BooleanField(required=False)
    authorize_payment = serializers.BooleanField(required=False)
    authorize_l342 = serializers.BooleanField(required=False)
    authorize_network_access = serializers.BooleanField(required=False)

    geographic_area = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    connection_nature = serializers.ChoiceField(choices=[c[0] for c in EnedisMandate.ConnectionNature.choices], required=False, allow_null=True, allow_blank=True)

    # Signatures (optionnel: data URL ou fichier traité côté vue appelante)
    client_signature_signer_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_signature = serializers.ImageField(required=False, allow_null=True)
    client_signature_data_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    client_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    installer_signature_signer_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    installer_signature = serializers.ImageField(required=False, allow_null=True)
    installer_signature_data_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    installer_location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Ajustement layout optionnel
    y_offset_mm = serializers.FloatField(required=False, default=8.0)

    def get_items(self) -> List[Dict[str, Any]]:
        """Convertit les champs validés en items overlay (texte/radio/checkbox/image).
        Les coordonnées seront à ajuster finement en mm; placeholders inclus ci-dessous.
        """
        v = getattr(self, 'validated_data', {})

        items: List[Dict[str, Any]] = []
        def text(x, y, value):
            items.append({"type": "text", "x": x, "y": y, "value": value})
        def radio(x, y, checked, r=1.5):
            items.append({"type": "radio", "x": x, "y": y, "value": bool(checked), "r": r})
        def check(x, y, checked):
            items.append({"type": "checkbox", "x": x, "y": y, "value": bool(checked)})
        def image(x, y, file_or_bytes, w=None, h=None):
            items.append({"type": "image", "x": x, "y": y, "value": file_or_bytes, "w": w, "h": h})

        # NOTE: Les coordonnées ci-dessous sont à calibrer en mm sur le template Enedis-FOR-RAC_02E.pdf
        # 1) Civilité radio: MR vs MME (ex: deux positions sur la même ligne)
        client_type = (v.get("client_type") or "").strip().lower()
        radio(19, 373, client_type == "individual")
        radio(19, 399.5, client_type == "company")
        radio(70, 399.5, client_type == "collectivity")

        if(client_type == "individual"):
            civ = (v.get("client_civility") or "").strip().lower()
            radio(24, 379, civ == "mme")
            radio(51.5, 379, civ == "mr")
            text(60, 386, v.get("client_name") or "")
            text(60, 391, v.get("client_address") or "")
        else:
            # 3) Société/Collectivité
            text(75, 407, v.get("client_company_name") or "")
            text(75, 413, v.get("client_company_siret") or "")
            text(75, 423, v.get("client_company_represented_by_name") or "")
            text(75, 428, v.get("client_company_represented_by_role") or "")

        contractor_type = (v.get("contractor_type") or "").strip().lower()
        radio(19, 454, contractor_type == "individual")
        radio(19, 480, contractor_type == "company")
        radio(70, 480, contractor_type == "collectivity")

        if(contractor_type == "individual"):
            civ = (v.get("contractor_civility") or "").strip().lower()
            radio(24, 460, civ == "mme")
            radio(51.5, 460, civ == "mr")
            text(60, 467, v.get("contractor_name") or "")
            text(60, 472, v.get("contractor_address") or "")
        else:
            # 3) Société/Collectivité
            text(75, 488, v.get("contractor_company_name") or "")
            text(75, 494, v.get("contractor_company_siret") or "")
            text(75, 504, v.get("contractor_company_represented_by_name") or "")
            text(75, 509, v.get("contractor_company_represented_by_role") or "")

        # 5) Mandat type (radio)
        mdt = (v.get("mandate_type") or "").strip().lower()
        radio(19, 637, mdt == "simple")
        radio(19, 672.5, mdt == "special")

        # 6) Autorisations (checkbox)
        check(19, 752, v.get("authorize_signature"))
        check(19, 792, v.get("authorize_payment"))
        check(19, 799.5, v.get("authorize_l342"))
        check(19, 811.5, v.get("authorize_network_access"))

        # 7) Localisation
        text(66, 1021, v.get("geographic_area") or "")

        # 8) Nature de raccordement (radio)
        cn = (v.get("connection_nature") or "").strip().lower()
        connection_nature = ""
        match cn:
            case "indiv_or_group_housing":
                connection_nature = "Raccordement de logements individuels ou groupés"
            case "commercial_or_production":
                connection_nature = "Locaux commerciaux/professionnels ou installation de production"
            case "branch_modification":
                connection_nature = "Modification de branchement"
            case "power_change_or_ev":
                connection_nature = "Modification de la puissance de raccordement / IRVE"
        text(66, 1027, connection_nature)

        # 9) Signatures (images si fournies)
        text(35, 1244, v.get("client_signature_signer_name") or "")
        text(110, 1244, v.get("installer_signature_signer_name") or "")
        text(35, 1253, v.get("client_location") or "")
        text(110, 1253, f"{v.get("installer_location")} le {timezone.now().strftime("%d/%m/%Y")}" or "")
        client_sig_val = v.get("client_signature") or v.get("client_signature_data_url")
        if client_sig_val:
            image(35, 1260, client_sig_val, w=30, h=15)
        installer_sig_val = v.get("installer_signature") or v.get("installer_signature_data_url")
        if installer_sig_val:
            image(110, 1260, installer_sig_val, w=80, h=35)

        return items
