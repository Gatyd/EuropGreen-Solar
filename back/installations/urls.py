from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormViewSet
from .commission_views import CommissionViewSet

router = DefaultRouter()
router.register(r'forms', FormViewSet, basename='installations-forms')
router.register(r'commissions', CommissionViewSet, basename='installations-commissions')

urlpatterns = [
	path('installations/', include(router.urls)),
]
