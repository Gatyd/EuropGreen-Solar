"""
URLs pour la plateforme d'administration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailLogViewSet, AuditLogViewSet
from .dashboard_views import DashboardViewSet
from .reports_views import ReportsViewSet

router = DefaultRouter()
router.register(r'email-logs', EmailLogViewSet, basename='email-log')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'reports', ReportsViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
