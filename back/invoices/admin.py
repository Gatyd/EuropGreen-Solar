from django.contrib import admin
from .models import Invoice, InvoiceLine, Installment, Payment


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "installation", "issue_date", "total", "status")
    list_filter = ("status", "issue_date", "currency")
    search_fields = ("number", "installation__client_last_name", "installation__client_first_name")
    inlines = [InvoiceLineInline, InstallmentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "date", "amount", "method")
    list_filter = ("method", "date")
    search_fields = ("invoice__number", "reference")
