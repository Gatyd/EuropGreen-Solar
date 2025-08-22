from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, QuoteViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'quotes', QuoteViewSet, basename='quotes')

urlpatterns = router.urls
