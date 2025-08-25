from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q
from authentication.permissions import HasOfferAccess

from .models import Product, Quote, QuoteSignature, QuoteLine
from .serializers import (
    ProductSerializer,
    QuoteSerializer,
    QuoteNegotiationSerializer,
    QuoteNegotiationReplySerializer,
)
from django.core.files.base import ContentFile
import asyncio
from typing import Optional
import logging
from django.http import HttpRequest
from django.conf import settings
from EuropGreenSolar.email_utils import send_mail

async def _render_quote_pdf_playwright_async(quote: Quote, request: Optional[HttpRequest] = None) -> bytes:
    
    from playwright.async_api import async_playwright

    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
    url = f"{base_url}/print/quotes/{quote.id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context()
        try:
            # Authentification côté front via cookies: on essaie d'abord de copier ceux de la requête en cours
            cookie_payloads = []
            try:
                if request is not None:
                    access_name = getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token')
                    refresh_name = getattr(settings, 'REFRESH_TOKEN_COOKIE_NAME', 'refresh_token')
                    for name in (access_name, refresh_name):
                        val = request.COOKIES.get(name)
                        if val:
                            cookie_payloads.append({
                                'name': name,
                                'value': val,
                                'url': base_url,
                                'path': '/',
                            })
            except Exception:
                # ne bloque pas si indisponible
                pass

            # Si aucun cookie n'a été trouvé, repli: émettre un token d'accès pour le créateur du devis
            if not cookie_payloads:
                try:
                    from rest_framework_simplejwt.tokens import AccessToken
                    if getattr(quote, 'created_by', None):
                        token = str(AccessToken.for_user(quote.created_by))
                        cookie_payloads.append({
                            'name': getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token'),
                            'value': token,
                            'url': base_url,
                            'path': '/',
                        })
                except Exception:
                    pass

            if cookie_payloads:
                try:
                    await context.add_cookies(cookie_payloads)
                except Exception:
                    # continuer sans auth si quelque chose cloche
                    pass

            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")
            pdf_bytes = await page.pdf(format="A4", print_background=True, margin={"top":"10mm","right":"10mm","bottom":"10mm","left":"10mm"})
            return pdf_bytes
        finally:
            try:
                await context.close()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass


def render_quote_pdf(quote: Quote, request: Optional[HttpRequest] = None) -> bytes:
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            # Exécuter dans une nouvelle boucle si on est déjà dans un event loop
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(_render_quote_pdf_playwright_async(quote, request))
            finally:
                new_loop.close()
        else:
            return asyncio.run(_render_quote_pdf_playwright_async(quote, request))
    except Exception as e:
        print(f"Error rendering PDF with Playwright: {e}")
        return None


def _ensure_quote_pdf(quote: Quote, request: Optional[HttpRequest] = None):
    """Generate and attach a PDF to the quote if not present."""
    if getattr(quote, 'pdf', None):
        try:
            if quote.pdf and quote.pdf.name:
                return
        except Exception:
            pass
    pdf_bytes = render_quote_pdf(quote, request=request)
    if pdf_bytes:
        filename = f"{quote.number}.pdf"
        quote.pdf.save(filename, ContentFile(pdf_bytes), save=True)


def _build_quote_links(offer_id: str) -> dict:
    base_front = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
    return {
        'link_negotiation': f"{base_front}/offers/{offer_id}?action=negotiation",
        'link_signature': f"{base_front}/offers/{offer_id}?action=signature",
    }


def _send_quote_sent_email(quote: Quote, request: Optional[HttpRequest] = None, predecessor_number: Optional[str] = None):
    """Send the standard quote email using quote_sent.html, optionally indicating a predecessor invalidation."""
    offer = quote.offer
    links = _build_quote_links(offer.id)
    ctx = {
        "client_name": f"{offer.first_name} {offer.last_name}",
        "quote_number": quote.number,
        "quote_total": quote.total,
        "quote_valid_until": quote.valid_until,
        **links,
    }
    subject = f"Votre devis {quote.number} – Europ'Green Solar"
    if predecessor_number:
        ctx['predecessor_number'] = predecessor_number
        subject = f"Votre nouveau devis {quote.number} – Europ'Green Solar"

    attachments = []
    try:
        if quote.pdf and quote.pdf.path:
            attachments.append(quote.pdf.path)
    except Exception:
        pass

    return send_mail(
        template="emails/quote/quote_sent.html",
        context=ctx,
        subject=subject,
        to=offer.email,
        attachments=attachments if attachments else None,
    )


logger = logging.getLogger(__name__)


def _create_quote_new_version(previous: Quote, payload: dict, user=None) -> Quote:
    """Create a new quote version via ORM (bypassing serializer unique validation), copy or apply lines, and recalc totals."""
    from decimal import Decimal
    from datetime import date

    title = payload.get('title', previous.title) or ''
    valid_until = payload.get('valid_until', previous.valid_until)
    if isinstance(valid_until, str) and valid_until:
        try:
            valid_until = date.fromisoformat(valid_until)
        except Exception:
            valid_until = previous.valid_until
    try:
        tax_rate = Decimal(str(payload.get('tax_rate', previous.tax_rate)))
    except Exception:
        tax_rate = previous.tax_rate
    notes = payload.get('notes', previous.notes) or ''

    extra = {}
    if user is not None and getattr(user, 'is_authenticated', False):
        extra['created_by'] = user
        extra['updated_by'] = user

    new_quote = Quote.objects.create(
        offer=previous.offer,
        predecessor=previous,
        status=Quote.Status.DRAFT,
        title=title,
        valid_until=valid_until,
        tax_rate=tax_rate,
        notes=notes,
        negociations='',
        **extra,
    )

    lines = payload.get('lines')
    created_lines = 0
    if not lines:
        for idx, ol in enumerate(previous.lines.order_by('position', 'created_at')):
            QuoteLine.objects.create(
                quote=new_quote,
                position=ol.position or idx,
                product_type=ol.product_type,
                name=ol.name,
                description=ol.description,
                unit_price=ol.unit_price,
                cost_price=ol.cost_price,
                quantity=ol.quantity,
                discount_rate=ol.discount_rate,
            )
            created_lines += 1
    else:
        for idx, l in enumerate(lines or []):
            try:
                up = Decimal(str(l.get('unit_price', 0)))
            except Exception:
                up = Decimal('0')
            try:
                cp = Decimal(str(l.get('cost_price', 0)))
            except Exception:
                cp = Decimal('0')
            try:
                qty = Decimal(str(l.get('quantity', 0)))
            except Exception:
                qty = Decimal('0')
            try:
                disc = Decimal(str(l.get('discount_rate', 0)))
            except Exception:
                disc = Decimal('0')
            QuoteLine.objects.create(
                quote=new_quote,
                position=l.get('position', idx),
                product_type=l.get('product_type') or 'other',
                name=l.get('name') or '',
                description=l.get('description') or '',
                unit_price=up,
                cost_price=cp,
                quantity=qty,
                discount_rate=disc,
            )
            created_lines += 1

    # Recalculate totals
    subtotal = sum((line.line_total for line in new_quote.lines.all()), Decimal('0'))
    new_quote.subtotal = subtotal
    try:
        tax_factor = (new_quote.tax_rate or Decimal('0')) / Decimal('100')
    except Exception:
        tax_factor = Decimal('0')
    new_quote.total = (new_quote.subtotal * (Decimal('1') + tax_factor)).quantize(Decimal('0.01'))
    new_quote.save(update_fields=['subtotal', 'total'])

    logger.info("Created new quote version", extra={
        'previous_id': str(previous.id),
        'new_id': str(new_quote.id),
        'offer': str(previous.offer_id),
        'version': new_quote.version,
        'lines': created_lines,
    })

    return new_quote

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
    permission_classes = [HasOfferAccess]
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
    permission_classes = [HasOfferAccess]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_permissions(self):
        if self.action in ["retrieve", "negotiate", "sign"]:
            # Actions publiques, pas de permissions requises
            return []
        return super().get_permissions()

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
        pdf_bytes = render_quote_pdf(quote, request=self.request)
        if pdf_bytes:
            filename = f"{quote.number}.pdf"
            quote.pdf.save(filename, ContentFile(pdf_bytes), save=True)
        # rien à retourner ici, DRF gère la réponse via serializer

    def perform_update(self, serializer):
        # Supprimer l'ancien PDF si présent pour éviter les suffixes automatiques
        instance: Quote = self.get_object()
        old_pdf_name = instance.pdf.name if getattr(instance, "pdf", None) else None
        quote = serializer.save()
        if old_pdf_name:
            try:
                # delete without updating the model (we'll save a new file next)
                instance.pdf.delete(save=False)
            except Exception:
                pass
        # Régénérer le PDF et enregistrer sous le même nom logique
        pdf_bytes = render_quote_pdf(quote, request=self.request)
        if pdf_bytes:
            filename = f"{quote.number}.pdf"
            quote.pdf.save(filename, ContentFile(pdf_bytes), save=True)

    @action(detail=True, methods=["post"], url_path="send-new-version")
    def send_new_version(self, request, pk=None):
        # Nouvelle version via serializer + envoi mail standard avec mention d'invalidation
        previous = self.get_object()
        offer = previous.offer
        if not offer.email:
            return Response({"detail": "Aucune adresse email client"}, status=status.HTTP_400_BAD_REQUEST)
        payload = request.data.copy()
        try:
            logger.info("send_new_version payload", extra={
                'previous_id': str(previous.id),
                'offer': str(offer.id),
                'has_lines': 'lines' in payload,
                'lines_len': len(payload.get('lines', []) or [])
            })
        except Exception:
            pass
        user = getattr(request, 'user', None)

        new_quote = _create_quote_new_version(previous, payload, user=user)
        _ensure_quote_pdf(new_quote, request=request)

        ok, msg = _send_quote_sent_email(new_quote, request=request, predecessor_number=previous.number)
        if not ok:
            return Response({"detail": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        from billing.models import Quote as QuoteModel
        new_quote.status = QuoteModel.Status.SENT
        new_quote.save(update_fields=["status"])
        from offers.models import Offer as OfferModel
        offer.status = OfferModel.Status.QUOTE_SENT
        offer.save(update_fields=["status"])

        return Response(self.get_serializer(new_quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="send")
    def send_quote(self, request, pk=None):
        quote = self.get_object()
        offer = quote.offer
        # Vérifications minimales
        if not offer.email:
            return Response({"detail": "Aucune adresse email client"}, status=status.HTTP_400_BAD_REQUEST)
        # S'assurer qu'un PDF est présent
        _ensure_quote_pdf(quote, request=self.request)

        ok, msg = _send_quote_sent_email(quote, request=self.request)
        if not ok:
            print(msg)
            return Response({"detail": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Mises à jour des statuts
        from billing.models import Quote as QuoteModel  # éviter l'import circulaire
        quote.status = QuoteModel.Status.SENT
        quote.save(update_fields=["status"])
        # statut de l'offre
        from offers.models import Offer as OfferModel
        offer.status = OfferModel.Status.QUOTE_SENT
        offer.save(update_fields=["status"])

        data = self.get_serializer(quote).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="negotiate", permission_classes=[], authentication_classes=[])  # public
    def negotiate(self, request, pk=None):
        quote = self.get_object()
        # Règle métier: seule la dernière version d'une offre peut être négociée
        latest = Quote.objects.filter(offer=quote.offer).order_by("-version").first()
        if not latest or latest.id != quote.id:
            return Response({"detail": "Seul le dernier devis est négociable."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = QuoteNegotiationSerializer(data=request.data, context={'quote': quote})
        serializer.is_valid(raise_exception=True)
        quote = serializer.save()
        quote.status = Quote.Status.PENDING
        quote.save()
        return Response({"detail": "Message enregistré"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reply")
    def reply_current(self, request, pk=None):
        quote = self.get_object()
        # Vérifier que c'est la dernière version
        latest = Quote.objects.filter(offer=quote.offer).order_by("-version").first()
        if not latest or latest.id != quote.id:
            return Response({"detail": "Seul le dernier devis est modifiable."}, status=status.HTTP_400_BAD_REQUEST)
        ser = QuoteNegotiationReplySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        reply = ser.validated_data['reply']

        # Contexte email
        offer = quote.offer
        subject = f"Réponse à votre demande – {quote.number}"
        ctx = {
            'quote_number': quote.number,
            'client_message': quote.negociations or '',
            'reply_message': reply,
            'quote_total': quote.total,
            'quote_valid_until': quote.valid_until,
        }
        # Liens d'action (négociation / signature)
        base_front = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
        ctx['link_negotiation'] = f"{base_front}/offers/{offer.id}?action=negotiation"
        ctx['link_signature'] = f"{base_front}/offers/{offer.id}?action=signature"
        # Pièce jointe
        attachments = []
        try:
            if quote.pdf and quote.pdf.path:
                attachments.append(quote.pdf.path)
        except Exception:
            pass

        ok, msg = send_mail(
            template='emails/quote/quote_negotiation_reply.html',
            context=ctx,
            subject=subject,
            to=offer.email,
            attachments=attachments if attachments else None,
        )
        if not ok:
            return Response({"detail": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Remise à zéro des négociations et statut sent
        quote.negociations = ''
        quote.status = Quote.Status.SENT
        quote.save(update_fields=['negociations', 'status'])
        return Response(self.get_serializer(quote).data)

    @action(detail=True, methods=["post"], url_path="reply-new-version")
    def reply_new_version(self, request, pk=None):
        previous = self.get_object()
        # Vérifier que c'est la dernière version
        latest = Quote.objects.filter(offer=previous.offer).order_by("-version").first()
        if not latest or latest.id != previous.id:
            return Response({"detail": "Seul le dernier devis est modifiable."}, status=status.HTTP_400_BAD_REQUEST)

        # Réponse séparée du payload devis
        reply_ser = QuoteNegotiationReplySerializer(data={'reply': request.data.get('reply', '')})
        reply_ser.is_valid(raise_exception=True)
        reply = reply_ser.validated_data['reply']
        payload = request.data.copy()
        try:
            logger.info("reply_new_version payload", extra={
                'previous_id': str(previous.id),
                'offer': str(previous.offer_id),
                'has_lines': 'lines' in payload,
                'lines_len': len(payload.get('lines', []) or [])
            })
        except Exception:
            pass

        user = getattr(request, 'user', None)
        new_quote = _create_quote_new_version(previous, payload, user=user)
        _ensure_quote_pdf(new_quote, request=self.request)

        # Envoyer email avec le nouveau PDF
        offer = new_quote.offer
        subject = f"Réponse à votre demande – {new_quote.number}"
        ctx = {
            'quote_number': new_quote.number,
            'client_message': previous.negociations or '',
            'reply_message': reply,
            'quote_total': new_quote.total,
            'quote_valid_until': new_quote.valid_until,
        }
        base_front = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
        ctx['link_negotiation'] = f"{base_front}/offers/{offer.id}?action=negotiation"
        ctx['link_signature'] = f"{base_front}/offers/{offer.id}?action=signature"
        attachments = []
        try:
            if new_quote.pdf and new_quote.pdf.path:
                attachments.append(new_quote.pdf.path)
        except Exception:
            pass
        ok, msg = send_mail(
            template='emails/quote/quote_negotiation_reply.html',
            context=ctx,
            subject=subject,
            to=offer.email,
            attachments=attachments if attachments else None,
        )
        if not ok:
            return Response({"detail": msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Remise à zéro des negociations sur l’ancienne version et statut sent
        new_quote.status = Quote.Status.SENT
        new_quote.save(update_fields=['status'])

        return Response(self.get_serializer(new_quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="sign", permission_classes=[], authentication_classes=[])
    def sign(self, request, pk=None):
        quote = self.get_object()
        # Valider dernière version
        latest = Quote.objects.filter(offer=quote.offer).order_by("-version").first()
        if not latest or latest.id != quote.id:
            return Response({"detail": "Seul le dernier devis est signable."}, status=status.HTTP_400_BAD_REQUEST)
        # Déjà signé
        if getattr(quote, "signature", None):
            return Response({"detail": "Ce devis est déjà signé."}, status=status.HTTP_400_BAD_REQUEST)
        # Optionnel: vérifier le statut
        if quote.status in (Quote.Status.ACCEPTED, Quote.Status.DECLINED):
            return Response({"detail": "Ce devis n'est pas dans un état signable."}, status=status.HTTP_400_BAD_REQUEST)

        signer_name = (request.data.get("signer_name") or "").strip()
        signature_image_b64 = request.data.get("signature_image")  # data URL ou base64 pur
        signature_file = request.FILES.get("signature_file")  # upload direct
        if not signer_name:
            return Response({"detail": "Nom du signataire requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Récup IP et UA (en tenant compte des proxys) et normalisation
        def _get_client_ip(req):
            x_real_ip = req.META.get("HTTP_X_REAL_IP")
            if x_real_ip:
                ip_ = x_real_ip.strip()
            else:
                xff = req.META.get("HTTP_X_FORWARDED_FOR")
                if xff:
                    ip_ = xff.split(",")[0].strip()
                else:
                    ip_ = req.META.get("REMOTE_ADDR")
            # Normaliser IPv6 loopback et IPv4-mappée
            if ip_ == "::1":
                ip_ = "127.0.0.1"
            if ip_ and ip_.startswith("::ffff:"):
                ip_ = ip_.split(":")[-1]
            return ip_

        ip = _get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        sig = QuoteSignature(quote=quote, signer_name=signer_name, ip_address=ip, user_agent=ua)

        # 1) Fichier uploadé prioritaire
        if signature_file:
            sig.signature_image.save(signature_file.name, signature_file, save=False)
        # 2) Sinon data URL/base64
        elif signature_image_b64 and isinstance(signature_image_b64, str):
            import base64, re
            try:
                match = re.match(r"^data:image/(png|jpeg|jpg);base64,(.+)$", signature_image_b64)
                if match:
                    ext = match.group(1)
                    raw_b64 = match.group(2)
                else:
                    raw_b64 = signature_image_b64
                    ext = "png"
                data = base64.b64decode(raw_b64)
                fname = f"signature-{quote.id}." + ("jpg" if ext in ("jpeg", "jpg") else "png")
                sig.signature_image.save(fname, ContentFile(data), save=False)
            except Exception:
                return Response({"detail": "Image de signature invalide."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Aucune image de signature fournie."}, status=status.HTTP_400_BAD_REQUEST)

        sig.save()

        # Maj des statuts
        from offers.models import Offer as OfferModel
        quote.status = Quote.Status.ACCEPTED
        quote.offer.status = OfferModel.Status.QUOTE_SIGNED
        quote.offer.save(update_fields=["status"])
        quote.save(update_fields=["status"])

        data = QuoteSerializer(quote, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)
