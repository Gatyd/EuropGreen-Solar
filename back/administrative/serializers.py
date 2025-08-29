from rest_framework import serializers
from .models import Cerfa16702, ElectricalDiagram, EnedisMandate

class Cerfa16702Serializer(serializers.ModelSerializer):
    class Meta:
        model = Cerfa16702
        fields = '__all__'
        read_only_fields = ('id', 'form', 'created_by', 'created_at', 'updated_at')

class ElectricalDiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricalDiagram
        fields = '__all__'

class EnedisMandateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnedisMandate
        fields = '__all__'
