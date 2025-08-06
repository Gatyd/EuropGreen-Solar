from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AdminUserViewSet, CurrentUserView

router = DefaultRouter()
router.register(r'users/me', UserViewSet)
router.register(r'users', AdminUserViewSet, basename='users')

app_name = 'users'

urlpatterns = [
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('', include(router.urls)),
]
