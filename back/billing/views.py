from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q

from .models import Product, Quote, QuoteSignature, QuoteLine
from .serializers import ProductSerializer, QuoteSerializer, QuoteSignatureSerializer
from django.core.files.base import ContentFile
from io import BytesIO
import asyncio
from django.conf import settings

def _render_quote_pdf_reportlab(quote: Quote) -> bytes:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
    except Exception:
        return b""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, "DEVIS")
    y -= 10 * mm
    c.setFont("Helvetica", 10)
    client = f"A: {quote.offer.first_name} {quote.offer.last_name}"
    c.drawString(20 * mm, y, client)
    y -= 5 * mm
    c.drawString(20 * mm, y, quote.offer.address)
    y -= 10 * mm
    c.drawString(140 * mm, height - 20 * mm, f"N°: {quote.number}")
    c.drawString(140 * mm, height - 25 * mm, f"Date: {quote.created_at.date()}")
    if quote.valid_until:
        c.drawString(140 * mm, height - 30 * mm, f"Valide jusqu'au: {quote.valid_until}")
    y -= 10 * mm
    if quote.title:
        c.setFont("Helvetica", 9)
        c.drawString(20 * mm, y, quote.title)
        y -= 8 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(20 * mm, y, "DESCRIPTION")
    c.drawRightString(130 * mm, y, "QTE")
    c.drawRightString(160 * mm, y, "PRIX")
    c.drawRightString(180 * mm, y, "REMISE %")
    c.drawRightString(200 * mm, y, "MONTANT")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    for line in quote.lines.order_by("position", "created_at"):
        if y < 20 * mm:
            c.showPage(); y = height - 20 * mm
        c.drawString(20 * mm, y, line.name[:80])
        c.drawRightString(130 * mm, y, f"{line.quantity}")
        c.drawRightString(160 * mm, y, f"{line.unit_price:.2f}")
        c.drawRightString(180 * mm, y, f"{line.discount_rate:.2f}")
        c.drawRightString(200 * mm, y, f"{line.line_total:.2f}")
        y -= 5 * mm
        if line.description:
            for chunk in line.description.split("\n"):
                if y < 20 * mm:
                    c.showPage(); y = height - 20 * mm
                c.setFont("Helvetica", 8)
                c.drawString(22 * mm, y, chunk[:100])
                c.setFont("Helvetica", 9)
                y -= 4 * mm
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(180 * mm, y, "TOTAL H.T.")
    c.setFont("Helvetica", 9)
    c.drawRightString(200 * mm, y, f"{quote.subtotal:.2f} €")
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(180 * mm, y, f"TVA {quote.tax_rate:.0f}%")
    c.setFont("Helvetica", 9)
    c.drawRightString(200 * mm, y, f"{(quote.total - quote.subtotal):.2f} €")
    y -= 5 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(180 * mm, y, "TOTAL (EUR)")
    c.setFont("Helvetica", 10)
    c.drawRightString(200 * mm, y, f"{quote.total:.2f} €")
    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


async def _render_quote_pdf_playwright_async(quote: Quote) -> bytes:
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return _render_quote_pdf_reportlab(quote)

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/quotes/{quote.id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        # Auth via cookie JWT si possible
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            if getattr(quote, 'created_by', None):
                token = str(AccessToken.for_user(quote.created_by))
                # Déposer le cookie d'accès sur le domaine du front
                await context.add_cookies([
                    {
                        'name': getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token'),
                        'value': token,
                        'url': base_url,
                    }
                ])
        except Exception:
            pass
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        pdf_bytes = await page.pdf(format="A4", print_background=True, margin={"top":"10mm","right":"10mm","bottom":"10mm","left":"10mm"})
        await browser.close()
        return pdf_bytes


def render_quote_pdf(quote: Quote) -> bytes:
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # Exécuter dans une nouvelle boucle si on est déjà dans un event loop
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_quote_pdf_playwright_async(quote))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_quote_pdf_playwright_async(quote))
    except Exception:
        return _render_quote_pdf_reportlab(quote)


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

    def perform_create(self, serializer):
        # enregistre en taggant l'utilisateur
        user = getattr(self.request, 'user', None)
        extra = {}
        if user and user.is_authenticated:
            extra['created_by'] = user
            extra['updated_by'] = user
        quote = serializer.save(**extra)
        # Générer le PDF et l'attacher
        pdf_bytes = render_quote_pdf(quote)
        if pdf_bytes:
            filename = f"{quote.number}.pdf"
            quote.pdf.save(filename, ContentFile(pdf_bytes), save=True)
        # rien à retourner ici, DRF gère la réponse via serializer

    def perform_update(self, serializer):
        quote = serializer.save()
        # Régénérer le PDF et écraser l'ancien
        pdf_bytes = render_quote_pdf(quote)
        if pdf_bytes:
            filename = f"{quote.number}.pdf"
            # storage.save écrase car on réutilise le même nom dans FileField.save
            quote.pdf.save(filename, ContentFile(pdf_bytes), save=True)

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
