from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Cerfa16702ViewSet

router = DefaultRouter()
router.register(r'', Cerfa16702ViewSet)

urlpatterns = [
    path('administrative/', include(router.urls)),
]
