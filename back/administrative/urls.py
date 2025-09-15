from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Cerfa16702ViewSet, ElectricalDiagramViewSet, preview_cerfa_pdf
from .consuel_views import ConsuelPreviewAPIView, ConsuelViewSet

router = DefaultRouter()
router.register(r'cerfa16702', Cerfa16702ViewSet)
router.register(r'electrical-diagram', ElectricalDiagramViewSet)
router.register(r'consuel', ConsuelViewSet)

urlpatterns = [
    path('administrative/', include(router.urls)),
    path("administrative/cerfa/preview/", preview_cerfa_pdf, name="preview-cerfa"),
    path("administrative/consuel/preview/", ConsuelPreviewAPIView.as_view(), name="preview-consuel"),
]
