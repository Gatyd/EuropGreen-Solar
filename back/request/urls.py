from rest_framework.routers import DefaultRouter
from .views import ProspectRequestViewSet

router = DefaultRouter()
router.register(r'requests', ProspectRequestViewSet, basename='requests')

urlpatterns = router.urls
