from rest_framework import serializers
from .models import Offer


class OfferSerializer(serializers.ModelSerializer):
	class Meta:
		model = Offer
		fields = [
			'id', 'request', 'last_name', 'first_name', 'email', 'phone', 'address',
			'project_details', 'status', 'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'request', 'created_at', 'updated_at']
