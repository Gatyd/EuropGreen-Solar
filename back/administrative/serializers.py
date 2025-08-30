from rest_framework import serializers
from .models import Cerfa16702, ElectricalDiagram, EnedisMandate
from installations.models import Signature

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
