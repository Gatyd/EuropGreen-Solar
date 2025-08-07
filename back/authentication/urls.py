from django.urls import path,include
from .views import LoginUser, LogoutUser, RefreshTokenView, ForgotPasswordView, ResetPasswordView, ResendResetEmailView

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password_with_token'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('resend-reset-email/', ResendResetEmailView.as_view(), name='resend_reset_email'),
]