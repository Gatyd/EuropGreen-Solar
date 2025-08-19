from rest_framework import serializers
from .models import Offer
from billing.models import Quote
from billing.serializers import QuoteSerializer


class OfferSerializer(serializers.ModelSerializer):
	last_quote = serializers.SerializerMethodField()
	class Meta:
		model = Offer
		fields = [
			'id', 'request', 'last_name', 'first_name', 'email', 'phone', 'address',
			'project_details', 'status', 'created_at', 'updated_at', 'last_quote'
		]
		read_only_fields = ['id', 'request', 'created_at', 'updated_at']

	def get_last_quote(self, obj: Offer):
		quote = obj.quotes.order_by('-version', '-created_at').first()
		return QuoteSerializer(quote).data if quote else None
