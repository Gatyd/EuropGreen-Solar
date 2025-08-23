from rest_framework import viewsets, mixins
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q
from .models import Offer
from .serializers import OfferSerializer, OfferReturnToRequestSerializer
from authentication.permissions import HasOfferAccess
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


@extend_schema_view(
	list=extend_schema(summary="Liste des offres"),
	retrieve=extend_schema(summary="Détails d'une offre"),
	partial_update=extend_schema(summary="Mettre à jour partiellement une offre"),
)
class OfferViewSet(
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	viewsets.GenericViewSet,
):
	queryset = Offer.objects.all().order_by('-created_at')
	serializer_class = OfferSerializer
	parser_classes = [JSONParser, FormParser, MultiPartParser]
	permission_classes = [HasOfferAccess]

	def get_queryset(self):
		qs = Offer.objects.filter(installation_moved_at__isnull=True, returned_to_request_at__isnull=True).order_by('-created_at')
		status_param = self.request.query_params.get('status')
		if status_param:
			qs = qs.filter(status=status_param)

		created_from = self.request.query_params.get('created_from')
		created_to = self.request.query_params.get('created_to')
		if created_from:
			qs = qs.filter(created_at__date__gte=created_from)
		if created_to:
			qs = qs.filter(created_at__date__lte=created_to)

		search = self.request.query_params.get('search')
		if search:
			s = search.strip()
			qs = qs.filter(
				Q(first_name__icontains=s)
				| Q(last_name__icontains=s)
				| Q(email__icontains=s)
				| Q(phone__icontains=s)
				| Q(address__icontains=s)
			)
		return qs

	def get_permissions(self):
		# Rendre la route de détail publique (retrieve), le reste reste protégé
		if self.action == 'retrieve':
			return [AllowAny()]
		return super().get_permissions()
	
	@action(detail=True, methods=['post'],  url_path='return_to_request')
	def return_to_request(self, request, pk=None):
		# Validation de la payload
		serializer = OfferReturnToRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		request_status = serializer.validated_data['request_status']

		try:
			offer: Offer = self.get_object()
		except Offer.DoesNotExist:
			return Response({"detail": "Offre introuvable"}, status=status.HTTP_404_NOT_FOUND)

		prospect_request = offer.request
		# Mettre à jour les timestamps et le statut
		offer.returned_to_request_at = timezone.now()
		offer.save(update_fields=["returned_to_request_at", "updated_at"])

		prospect_request.converted_to_offer_at = None
		prospect_request.status = request_status
		prospect_request.save(update_fields=["converted_to_offer_at", "status", "updated_at"])

		return Response({"detail": "Offre retournée vers les demandes"}, status=status.HTTP_200_OK)
		
