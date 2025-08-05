from django.urls import path,include
from .views import LoginUser, LogoutUser, RefreshTokenView

urlpatterns = [
    path('login/', LoginUser.as_view()),
    path('token/refresh/', RefreshTokenView.as_view()),
    path('logout/', LogoutUser.as_view())
]