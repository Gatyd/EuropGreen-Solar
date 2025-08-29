from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Cerfa16702ViewSet

router = DefaultRouter()
router.register(r'cerfa16702', Cerfa16702ViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
