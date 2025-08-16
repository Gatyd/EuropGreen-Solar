from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import HasRequestsAccess
from .models import ProspectRequest
from .serializers import ProspectRequestSerializer


@extend_schema_view(
	list=extend_schema(summary="Liste des demandes (prospects)"),
	create=extend_schema(summary="Créer une demande"),
	retrieve=extend_schema(summary="Détails d'une demande"),
	partial_update=extend_schema(summary="Mettre à jour partiellement une demande"),
)
class ProspectRequestViewSet(
	mixins.ListModelMixin,
	mixins.CreateModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	viewsets.GenericViewSet,
):
	queryset = ProspectRequest.objects.select_related("assigned_to").all()
	serializer_class = ProspectRequestSerializer
	http_method_names = ["get", "post", "patch"]
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_permissions(self):
		"""
		Permissions personnalisées selon l'action :
		- create: tout le monde peut créer une demande (pas de permission spéciale)
		- autres actions: nécessite HasRequestsAccess
		"""
		if self.action == 'create':
			permission_classes = []  # Pas de permission requise pour la création
		else:
			permission_classes = [IsAuthenticated, HasRequestsAccess]
		
		return [permission() for permission in permission_classes]

	def get_queryset(self):
		# Pour la création, pas besoin de filtrer le queryset
		if self.action == 'create':
			return ProspectRequest.objects.none()  # Queryset vide pour la création
		
		user = self.request.user
		
		# Vérifier que l'utilisateur est authentifié pour les autres actions
		if not user.is_authenticated:
			return ProspectRequest.objects.none()
		
		# Portée de base selon le rôle
		if user.is_superuser:
			qs = ProspectRequest.objects.select_related("assigned_to").all()
		elif not user.is_staff:
			# Utilisateur non staff: ne voir que ses propres demandes via email
			qs = ProspectRequest.objects.select_related("assigned_to").filter(email=user.email)
		else:
			# Staff non-admin: ne voir que les demandes qui lui sont assignées
			qs = ProspectRequest.objects.select_related("assigned_to").filter(assigned_to_id=user.id)

		# Filtres additionnels
		status_param = self.request.query_params.get("status")
		if status_param:
			qs = qs.filter(status=status_param)

		assigned_to = self.request.query_params.get("assigned_to")
		if assigned_to:
			qs = qs.filter(assigned_to_id=assigned_to)

		created_from = self.request.query_params.get("created_from")
		created_to = self.request.query_params.get("created_to")
		if created_from:
			qs = qs.filter(created_at__date__gte=created_from)
		if created_to:
			qs = qs.filter(created_at__date__lte=created_to)

		search = self.request.query_params.get("search")
		if search:
			from django.db.models import Q
			qs = qs.filter(
				Q(first_name__icontains=search)
				| Q(last_name__icontains=search)
				| Q(email__icontains=search)
				| Q(phone__icontains=search)
			)

		return qs
