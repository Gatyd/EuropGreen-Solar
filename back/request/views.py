from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import HasRequestsAccess
from .models import ProspectRequest
from .serializers import ProspectRequestSerializer, ClientProspectRequestSerializer
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
	destroy=extend_schema(summary="Supprimer une demande"),
)
class ProspectRequestViewSet(viewsets.ModelViewSet):
	queryset = ProspectRequest.objects.select_related("assigned_to", "offer").all()
	serializer_class = ProspectRequestSerializer
	http_method_names = ["get", "post", "patch", "delete"]
	parser_classes = [MultiPartParser, FormParser, JSONParser]

	def get_permissions(self):
		"""Permissions dynamiques : IsAuthenticated pour tous, HasRequestsAccess si staff."""
		if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser):
			return [IsAuthenticated(), HasRequestsAccess()]
		return [IsAuthenticated()]

	def get_serializer_class(self):
		"""Utilise ClientProspectRequestSerializer pour les clients non-staff EN LECTURE SEULEMENT."""
		# Pour la création/modification, toujours utiliser ProspectRequestSerializer
		if self.action in ['create', 'update', 'partial_update']:
			return ProspectRequestSerializer
		
		# Pour la lecture (list, retrieve), utiliser ClientProspectRequestSerializer pour les clients
		if self.request.user.is_authenticated and not self.request.user.is_staff and not self.request.user.is_superuser:
			return ClientProspectRequestSerializer
		return ProspectRequestSerializer

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
			"status_display": instance.get_status_display(),
			"source_type_display": instance.get_source_type_display(),
		}
		subject = f"Nouvelle demande assignée – {instance.last_name} {instance.first_name}"
		return send_project_mail(
			template='emails/prospect/prospect_assigned.html',
			context=context,
			subject=subject,
			to=assignee.email,
		)

	def _send_source_notification_email(self, instance: ProspectRequest, source):
		"""Envoie l'email de notification à la source de la demande.

		Return: (success: bool, message: str) ou (None, message) si pas d'email.
		"""
		if not source or not getattr(source, 'email', None):
			return None, "Aucune source ou email non défini"
		context = {
			"prospect": instance,
			"source": source,
			"created_by": instance.created_by,
			"status_display": instance.get_status_display(),
			"source_type_display": instance.get_source_type_display(),
		}
		subject = f"Nouvelle demande vous concernant – {instance.last_name} {instance.first_name}"
		return send_project_mail(
			template='emails/prospect/prospect_assigned_source.html',
			context=context,
			subject=subject,
			to=source.email,
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
			# Utilisateur non staff (client): voir les demandes où il est source
			qs = ProspectRequest.objects.select_related("assigned_to", "offer").filter(source_id=user.id)
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
		user = self.request.user
		instance = serializer.save(created_by=user)
		# Envoi d'un email au chargé d'affaire (utilisateur assigné) s'il est défini
		try:
			success, msg = self._send_assignment_email(instance, instance.assigned_to)
			if success is False:
				print(f"Echec envoi email d'assignation: {msg}")
		except Exception as e:
			print(f"Erreur lors de l'envoi de l'email d'assignation: {e}")

		# Envoi d'un email à la source si définie et différente de l'utilisateur connecté
		try:
			if instance.source and instance.source.id != user.id:
				success, msg = self._send_source_notification_email(instance, instance.source)
				if success is False:
					print(f"Echec envoi email à la source: {msg}")
		except Exception as e:
			print(f"Erreur lors de l'envoi de l'email à la source: {e}")

		# Notification aux administrateurs (superusers) à la création
		try:
			User = get_user_model()
            # On cible les superusers actifs avec un email défini
			admins = list(
				User.objects.filter(is_superuser=True, is_active=True).exclude(email__isnull=True)
				.exclude(email="").exclude(email=user.email).values_list('email', flat=True)
			)
			if admins:
				context = {
					"prospect": instance,
					"created_by": instance.created_by,
					"status_display": instance.get_status_display(),
					"source_type_display": instance.get_source_type_display(),
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
		user = self.request.user
		# Mémoriser l'ancien assigné et l'ancienne source
		old_assignee_id = None
		old_source_id = None
		try:
			old_values = (
				ProspectRequest.objects.filter(pk=serializer.instance.pk)
				.values('assigned_to_id', 'source_id')
				.first()
			)
			if old_values:
				old_assignee_id = old_values.get('assigned_to_id')
				old_source_id = old_values.get('source_id')
		except Exception as e:
			print(f"Impossible de récupérer les anciennes valeurs: {e}")

		instance = serializer.save()

		# Comparer et envoyer si l'assigné a changé
		new_assignee = instance.assigned_to
		new_assignee_id = new_assignee.id if new_assignee else None
		if new_assignee_id and new_assignee_id != old_assignee_id:
			try:
				success, msg = self._send_assignment_email(instance, new_assignee)
				if success is False:
					print(f"Echec envoi email d'assignation (update): {msg}")
			except Exception as e:
				print(f"Erreur lors de l'envoi de l'email d'assignation (update): {e}")

		# Comparer et envoyer si la source a changé et est différente de l'utilisateur connecté
		new_source = instance.source
		new_source_id = new_source.id if new_source else None
		if new_source_id and new_source_id != old_source_id and new_source_id != user.id:
			try:
				success, msg = self._send_source_notification_email(instance, new_source)
				if success is False:
					print(f"Echec envoi email à la source (update): {msg}")
			except Exception as e:
				print(f"Erreur lors de l'envoi de l'email à la source (update): {e}")

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
