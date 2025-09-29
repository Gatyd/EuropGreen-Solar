from rest_framework import serializers
from .models import Offer
from billing.serializers import QuoteSerializer
from request.models import ProspectRequest

class OfferBaseSerializer(serializers.ModelSerializer):
	class Meta:
		model = Offer
		fields = [
			'id', 'last_name', 'first_name', 'email', 'phone', 'address', 'project_details'
		]
		read_only_fields = ['id']

class OfferSerializer(serializers.ModelSerializer):
	last_quote = serializers.SerializerMethodField()
	notes = serializers.ListField(child=serializers.DictField(), read_only=True)
	class Meta:
		model = Offer
		fields = [
			'id', 'request', 'last_name', 'first_name', 'email', 'phone', 'address',
			'project_details', 'notes', 'status', 'created_at', 'updated_at', 'last_quote'
		]
		read_only_fields = ['id', 'request', 'created_at', 'updated_at']

	def get_last_quote(self, obj: Offer):
		quote = obj.quotes.order_by('-version', '-created_at').first()
		if not quote:
			return None
		# Propager le contexte (request) pour construire des URLs absolues
		return QuoteSerializer(quote, context=self.context).data


class OfferReturnToRequestSerializer(serializers.Serializer):
	"""Serializer pour retourner une offre vers les demandes.

	Attendu:
	- request_status: nouveau statut de la demande (parmi ProspectRequest.Status)
	"""
	request_status = serializers.ChoiceField(choices=ProspectRequest.Status.choices)


class OfferAddNoteSerializer(serializers.Serializer):
	note = serializers.CharField(allow_blank=False, max_length=5000)
