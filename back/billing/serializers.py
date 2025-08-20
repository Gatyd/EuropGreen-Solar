from rest_framework import serializers
from .models import Product, Quote, QuoteLine, QuoteSignature
from django.db import transaction
from decimal import Decimal


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "type", "description", "unit_price", "cost_price", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuoteLineSerializer(serializers.ModelSerializer):
    source_product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    quote = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = QuoteLine
        fields = [
            "id",
            "quote",
            "source_product",
            "product_type",
            "name",
            "description",
            "unit_price",
            "cost_price",
            "quantity",
            "discount_rate",
            "line_total",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "quote", "line_total", "created_at", "updated_at"]
        extra_kwargs = {"quote": {"required": False}}


class QuoteSignatureSerializer(serializers.ModelSerializer):
    signature_image = serializers.SerializerMethodField()

    class Meta:
        model = QuoteSignature
        fields = [
            "id",
            "quote",
            "signer_name",
            "ip_address",
            "user_agent",
            "signed_at",
            "signature_image",
            "created_at",
        ]
        read_only_fields = ["id", "signed_at", "created_at"]

    def get_signature_image(self, obj: QuoteSignature):
        if not getattr(obj, "signature_image", None):
            return None
        try:
            url = obj.signature_image.url
        except Exception:
            return None
        request = self.context.get("request") if hasattr(self, "context") else None
        if request:
            return request.build_absolute_uri(url)
        return url


class QuoteSerializer(serializers.ModelSerializer):
    lines = QuoteLineSerializer(many=True, required=False)
    pdf = serializers.SerializerMethodField()
    signature = QuoteSignatureSerializer(read_only=True)

    class Meta:
        model = Quote
        fields = [
            "id",
            "number",
            "offer",
            "version",
            "predecessor",
            "status",
            "title",
            "notes",
            "currency",
            "valid_until",
            "subtotal",
            "discount_amount",
            "tax_rate",
            "total",
            "pdf",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
            "lines",
            "signature",
        ]
        read_only_fields = ["id", "number", "version", "subtotal", "discount_amount", "total", "pdf", "created_at", "updated_at",]
    # Aucun override requis; 'offer' reste obligatoire pour les créations classiques

    def get_pdf(self, obj: Quote):
        if not getattr(obj, 'pdf', None):
            return None
        try:
            url = obj.pdf.url
        except Exception:
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request:
            return request.build_absolute_uri(url)
        return url

    def _recalculate(self, quote: Quote):
        subtotal = sum((line.line_total for line in quote.lines.all()), Decimal("0"))
        quote.subtotal = subtotal.quantize(Decimal("0.01"))
        # discount_amount global laissé à 0 par défaut pour l'instant
        tax = (quote.tax_rate or Decimal("0")) / Decimal("100")
        quote.total = (quote.subtotal * (Decimal("1") + tax)).quantize(Decimal("0.01"))
        quote.save(update_fields=["subtotal", "total"])

    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop("lines", [])
        quote = Quote.objects.create(**validated_data)
        for idx, line in enumerate(lines_data):
            pos = line.pop("position", idx)
            QuoteLine.objects.create(quote=quote, position=pos, **line)
        self._recalculate(quote)
        return quote

    @transaction.atomic
    def update(self, instance: Quote, validated_data):
        lines_data = validated_data.pop("lines", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lines_data is not None:
            # stratégie simple: remplacer toutes les lignes si fourni
            instance.lines.all().delete()
            for idx, line in enumerate(lines_data):
                pos = line.pop("position", idx)
                QuoteLine.objects.create(quote=instance, position=pos, **line)
        self._recalculate(instance)
        return instance


class QuoteNegotiationSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False, allow_null=False, trim_whitespace=True)

    def validate_message(self, value: str):
        if not value or not value.strip():
            raise serializers.ValidationError("Message requis")
        if len(value) > 5000:
            raise serializers.ValidationError("Message trop long")
        return value.strip()

    def save(self, **kwargs):
        quote: Quote = self.context['quote']
        quote.notes = self.validated_data['message']
        # quote.status = Quote.Status.PENDING
        quote.offer.status = 'negotiation'
        quote.offer.save(update_fields=['status'])
        quote.save(update_fields=['notes'])
        return quote

class QuoteNegotiationReplySerializer(serializers.Serializer):
    reply = serializers.CharField(allow_blank=False, allow_null=False, trim_whitespace=True)

    def validate_reply(self, value: str):
        if not value or not value.strip():
            raise serializers.ValidationError("Réponse requise")
        if len(value) > 5000:
            raise serializers.ValidationError("Réponse trop longue")
        return value.strip()
