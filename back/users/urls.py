from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CurrentUserView, SupportView, CareerApplicationView, RoleViewSet
from .admin_views import AdminUserViewSet

router = DefaultRouter()
router.register(r'users/me', UserViewSet)
router.register(r'users', AdminUserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')

app_name = 'users'

urlpatterns = [
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/support/', SupportView.as_view(), name='support'),
    path('users/career/', CareerApplicationView.as_view(), name='career-application'),
    path('', include(router.urls)),
]
