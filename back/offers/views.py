from rest_framework import viewsets, mixins
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q
from .models import Offer
from .serializers import OfferSerializer


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
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		qs = Offer.objects.filter(installation_moved_at__isnull=True).order_by('-created_at')
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
