from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.settings import api_settings as jwt_settings


def set_jwt_access_cookie(response, access_token):
    """
    Définit le cookie d'access token JWT dans la réponse.
    """
    cookie_name = settings.ACCESS_TOKEN_COOKIE_NAME
    access_token_expiration = timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME
    
    response.set_cookie(
        cookie_name,
        access_token,
        expires=access_token_expiration,
        max_age=settings.ACCESS_TOKEN_MAX_AGE,
        secure=settings.TOKEN_COOKIE_SECURE,
        httponly=settings.TOKEN_COOKIE_HTTPONLY,
        samesite=settings.TOKEN_COOKIE_SAMESITE,
    )


def set_jwt_refresh_cookie(response, refresh_token):
    """
    Définit le cookie de refresh token JWT dans la réponse.
    """
    refresh_cookie_name = settings.REFRESH_TOKEN_COOKIE_NAME
    refresh_token_expiration = timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME
    
    response.set_cookie(
        refresh_cookie_name,
        refresh_token,
        expires=refresh_token_expiration,
        max_age=settings.REFRESH_TOKEN_MAX_AGE,
        secure=settings.TOKEN_COOKIE_SECURE,
        httponly=settings.TOKEN_COOKIE_HTTPONLY,
        samesite=settings.TOKEN_COOKIE_SAMESITE,
    )


def set_jwt_cookies(response, access_token, refresh_token):
    """
    Définit à la fois les cookies d'access token et de refresh token.
    """
    set_jwt_access_cookie(response, access_token)
    set_jwt_refresh_cookie(response, refresh_token)


def unset_jwt_cookies(response):
    """
    Supprime les cookies d'access token et de refresh token.
    """
    cookie_name = settings.ACCESS_TOKEN_COOKIE_NAME
    refresh_cookie_name = settings.REFRESH_TOKEN_COOKIE_NAME
    
    response.delete_cookie(
        cookie_name, 
        samesite=settings.TOKEN_COOKIE_SAMESITE
    )
    response.delete_cookie(
        refresh_cookie_name, 
        samesite=settings.TOKEN_COOKIE_SAMESITE
    )


def get_refresh_token_from_cookie(request):
    """
    Récupère le refresh token depuis les cookies de la requête.
    """
    return request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
