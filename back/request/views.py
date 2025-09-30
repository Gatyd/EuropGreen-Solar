from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import HasRequestsAccess
from .models import ProspectRequest
from .serializers import ProspectRequestSerializer
from django.db.models import Q
from EuropGreenSolar.email_utils import send_mail as send_project_mail
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from offers.models import Offer
from offers.serializers import OfferSerializer
from django.contrib.auth import get_user_model


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
	queryset = ProspectRequest.objects.select_related("assigned_to", "offer").all()
	serializer_class = ProspectRequestSerializer
	http_method_names = ["get", "post", "patch"]
	parser_classes = [MultiPartParser, FormParser, JSONParser]
	permission_classes = [IsAuthenticated, HasRequestsAccess]

	def _send_assignment_email(self, instance: ProspectRequest, assignee):
		"""Envoie l'email d'assignation au chargé d'affaire donné.

		Return: (success: bool, message: str) ou (None, message) si pas d'email.
		"""
		if not assignee or not getattr(assignee, 'email', None):
			return None, "Aucun assignee ou email non défini"
		context = {
			"prospect": instance,
			"assignee": assignee,
			"created_by": instance.created_by,
		}
		subject = f"Nouvelle demande assignée – {instance.last_name} {instance.first_name}"
		return send_project_mail(
			template='emails/prospect/prospect_assigned.html',
			context=context,
			subject=subject,
			to=assignee.email,
		)

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
			qs = ProspectRequest.objects.select_related("assigned_to", "offer")
		elif not user.is_staff:
			# Utilisateur non staff: ne voir que ses propres demandes via email
			qs = ProspectRequest.objects.select_related("assigned_to", "offer").filter(email=user.email)
		else:
			# Staff non-admin: ne voir que les demandes qui lui sont assignées
			qs = ProspectRequest.objects.select_related("assigned_to", "offer").filter(
					Q(assigned_to_id=user.id) | Q(created_by_id=user.id) | Q(source_id=user.id)
				)

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
			qs = qs.filter(
				Q(first_name__icontains=search)
				| Q(last_name__icontains=search)
				| Q(email__icontains=search)
				| Q(phone__icontains=search)
			)

		# Scopes de filtrage en fin de chaîne
		scope = self.request.query_params.get("scope")
		if scope == "prospects":
			# Prospects = demandes sans offre OU avec offre non déplacée vers installation
			qs = qs.filter(Q(offer__isnull=True) | Q(offer__installation_moved_at__isnull=True))
		elif scope == "all":
			# Toutes les demandes (dans la portée utilisateur)
			pass
		else:
			# Comportement historique: exclure celles déjà converties en offre
			qs = qs.filter(converted_to_offer_at__isnull=True)

		return qs
	
	def perform_create(self, serializer):
		instance = serializer.save(created_by=self.request.user)
		# Envoi d'un email au chargé d'affaire (utilisateur assigné) s'il est défini
		try:
			success, msg = self._send_assignment_email(instance, instance.assigned_to)
			if success is False:
				print(f"Echec envoi email d'assignation: {msg}")
		except Exception as e:
			print(f"Erreur lors de l'envoi de l'email d'assignation: {e}")

		# Notification aux administrateurs (superusers) à la création
		try:
			User = get_user_model()
            # On cible les superusers actifs avec un email défini
			admins = list(User.objects.filter(is_superuser=True, is_active=True).exclude(email__isnull=True).exclude(email="").values_list('email', flat=True))
			if admins:
				context = {
					"prospect": instance,
					"created_by": instance.created_by,
				}
				subject = f"Nouvelle demande créée – {instance.last_name} {instance.first_name}"
				# Envoyer à tous les admins en un seul email groupé
				success, msg = send_project_mail(
					template='emails/prospect/prospect_created_admin.html',
					context=context,
					subject=subject,
					to=admins,
				)
				if success is False:
					print(f"Echec envoi email admins (création): {msg}")
		except Exception as e:
			print(f"Erreur lors de l'envoi de l'email aux admins: {e}")

	def perform_update(self, serializer):
		"""Envoie un email si l'utilisateur assigné change (None->valeur ou valeur->autre valeur)."""
		# Mémoriser l'ancien assigné
		old_assignee_id = None
		try:
			old_assignee_id = (
				ProspectRequest.objects.filter(pk=serializer.instance.pk)
				.values_list('assigned_to_id', flat=True)
				.first()
			)
		except Exception as e:
			print(f"Impossible de récupérer l'ancien assigné: {e}")

		instance = serializer.save()

		# Comparer et envoyer si nécessaire
		new_assignee = instance.assigned_to
		new_assignee_id = new_assignee.id if new_assignee else None
		if new_assignee_id and new_assignee_id != old_assignee_id:
			try:
				success, msg = self._send_assignment_email(instance, new_assignee)
				if success is False:
					print(f"Echec envoi email d'assignation (update): {msg}")
			except Exception as e:
				print(f"Erreur lors de l'envoi de l'email d'assignation (update): {e}")

	@action(detail=True, methods=['post'], url_path='convert_to_offer')
	def convert_to_offer(self, request, pk=None):
		"""Convertit une demande en offre: marque la demande, crée l'offre et la lie."""
		try:
			instance: ProspectRequest = self.get_object()
			if instance.converted_to_offer_at:
				return Response({"detail": "Cette demande a déjà été convertie en offre."}, status=status.HTTP_400_BAD_REQUEST)

			# Créer l'offre avec les données de la demande si elle n'exite pas
			if not Offer.objects.filter(request=instance).exists():
				offer = Offer.objects.create(
					request=instance,
					last_name=instance.last_name,
					first_name=instance.first_name,
					email=instance.email,
					phone=instance.phone,
					address=instance.address
					# project_details libre pour le moment
				)
			else:
				offer = Offer.objects.get(request=instance)
				offer.returned_to_request_at = None
				offer.save(update_fields=["returned_to_request_at", "updated_at"])

			# Marquer la demande comme convertie
			instance.converted_to_offer_at = timezone.now()
			instance.save(update_fields=["converted_to_offer_at", "updated_at"])

			data = OfferSerializer(offer).data
			return Response(data, status=status.HTTP_201_CREATED)
		except Exception as e:
			print(e)
			return Response({"detail": f"Erreur de conversion: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
