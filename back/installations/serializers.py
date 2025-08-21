from rest_framework import serializers
from .models import Form


class FormSerializer(serializers.ModelSerializer):
	class Meta:
		model = Form
		fields = [
			'id',
			'offer',
			'client_first_name',
			'client_last_name',
			'client_address',
			'installation_power',
			'installation_type',
			'created_by',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
