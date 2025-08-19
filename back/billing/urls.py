from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, QuoteViewSet, QuoteSignatureViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'quotes', QuoteViewSet, basename='quotes')
router.register(r'quote-signatures', QuoteSignatureViewSet, basename='quote-signatures')

urlpatterns = router.urls
