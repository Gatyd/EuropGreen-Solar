from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Cerfa16702ViewSet, ElectricalDiagramViewSet, get_cerfa_fields, generate_cerfa_pdf, preview_cerfa_pdf

router = DefaultRouter()
router.register(r'cerfa16702', Cerfa16702ViewSet)
router.register(r'electrical-diagram', ElectricalDiagramViewSet)

urlpatterns = [
    path('administrative/', include(router.urls)),
    path("administrative/cerfa/fields/", get_cerfa_fields, name="cerfa-fields"),
    path("administrative/cerfa/fill/", generate_cerfa_pdf, name="generate-cerfa"),
    path("administrative/cerfa/preview/", preview_cerfa_pdf, name="preview-cerfa"),
]
