from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, PaymentViewSet, InstallmentViewSet


router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'installments', InstallmentViewSet, basename='installment')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls
