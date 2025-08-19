from django.contrib import admin
from .models import Product, Quote, QuoteLine, QuoteSignature


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("sku", "name", "type", "unit_price", "is_active")
	list_filter = ("type", "is_active")
	search_fields = ("sku", "name")


class QuoteLineInline(admin.TabularInline):
	model = QuoteLine
	extra = 0


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
	list_display = ("offer", "version", "status", "total", "created_at")
	list_filter = ("status",)
	search_fields = ("offer__id", "title")
	inlines = [QuoteLineInline]


@admin.register(QuoteSignature)
class QuoteSignatureAdmin(admin.ModelAdmin):
	list_display = ("quote", "signer_email", "ip_address", "signed_at")
