from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Cerfa16702ViewSet, ElectricalDiagramViewSet

router = DefaultRouter()
router.register(r'cerfa16702', Cerfa16702ViewSet)
router.register(r'electrical-diagram', ElectricalDiagramViewSet)

urlpatterns = [
    path('administrative/', include(router.urls)),
]
