from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q

from .models import Product, Quote, QuoteSignature
from .serializers import ProductSerializer, QuoteSerializer, QuoteSignatureSerializer


@extend_schema_view(
    list=extend_schema(summary="Liste des produits/services"),
    retrieve=extend_schema(summary="Détail d'un produit/service"),
    create=extend_schema(summary="Créer un produit/service"),
    partial_update=extend_schema(summary="Mettre à jour un produit/service"),
    destroy=extend_schema(summary="Désactiver/Supprimer un produit/service"),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
        t = self.request.query_params.get("type")
        if t:
            qs = qs.filter(type=t)
        active = self.request.query_params.get("active")
        if active in ("true", "false"):
            qs = qs.filter(is_active=(active == "true"))
        return qs


@extend_schema_view(
    list=extend_schema(summary="Liste des devis"),
    retrieve=extend_schema(summary="Détail d'un devis"),
    create=extend_schema(summary="Créer un devis"),
    partial_update=extend_schema(summary="Mettre à jour un devis"),
)
class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all().order_by("-created_at", "-version")
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        qs = super().get_queryset()
        offer = self.request.query_params.get("offer")
        if offer:
            qs = qs.filter(offer_id=offer)
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    @action(detail=True, methods=["post"], url_path="version")
    def create_new_version(self, request, pk=None):
        # Créer une nouvelle version basée sur la précédente
        previous = self.get_object()
        data = self.get_serializer(previous).data
        data["id"] = None
        data["predecessor"] = str(previous.id)
        data["status"] = Quote.Status.DRAFT
        # Les lignes sont retournées dans data["lines"] par le serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new = serializer.save()
        return Response(self.get_serializer(new).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    create=extend_schema(summary="Signer un devis (SES)"),
)
class QuoteSignatureViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = QuoteSignature.objects.select_related("quote").all()
    serializer_class = QuoteSignatureSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_create(self, serializer):
        quote = serializer.validated_data.get("quote")
        # Règle métier: seule la dernière version d'une offre peut être signée
        latest = Quote.objects.filter(offer=quote.offer).order_by("-version").first()
        if not latest or latest.id != quote.id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("Seul le dernier devis de l'offre peut être signé.")
        # Optionnel: forcer le statut à ACCEPTED lors de la signature
        quote.status = Quote.Status.ACCEPTED
        quote.save(update_fields=["status"])
        serializer.save()
