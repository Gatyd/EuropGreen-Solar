from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from django.conf import settings
from drf_spectacular.utils import extend_schema
from .serializers import LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, ResendResetEmailSerializer
from .cookie_utils import set_jwt_cookies, unset_jwt_cookies, get_refresh_token_from_cookie
from users.serializers import UserSerializer, User

class LoginUser(APIView):
    permission_classes = []
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user.last_login = now()
            if not user.accept_invitation:
                user.accept_invitation = True
            user.save()
            
            response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)
            set_jwt_cookies(response, str(refresh.access_token), str(refresh))
            
            return response
        return Response({"Connexion impossible": "Identifiants invalides"}, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = get_refresh_token_from_cookie(request)
        if not refresh_token:
            raise AuthenticationFailed('Refresh token non fourni.')

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            user = User.objects.get(id=token["user_id"])

        except TokenError:
            raise AuthenticationFailed('Token invalide ou expiré.')

        response = Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        set_jwt_cookies(response, access_token, str(RefreshToken.for_user(user)))

        return response
    
class LogoutUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        unset_jwt_cookies(response)
        return response


class ForgotPasswordView(APIView):
    """
    Vue pour demander la réinitialisation du mot de passe
    """
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    
    @extend_schema(
        summary="Demande de réinitialisation de mot de passe",
        description="Envoie un email avec un lien de réinitialisation si l'email existe dans le système",
        request=ForgotPasswordSerializer,
        responses={
            200: {"description": "Email envoyé avec succès"},
            400: {"description": "Données invalides"}
        }
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    Vue pour réinitialiser le mot de passe avec un token
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    
    @extend_schema(
        summary="Réinitialisation du mot de passe",
        description="Réinitialise le mot de passe en utilisant un token valide",
        request=ResetPasswordSerializer,
        responses={
            200: {"description": "Mot de passe réinitialisé avec succès"},
            400: {"description": "Token invalide ou données incorretes"}
        }
    )
    def post(self, request, token=None):
        # Si le token est dans l'URL, l'ajouter aux données
        data = request.data.copy()
        if token:
            data['token'] = token
        
        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendResetEmailView(APIView):
    """
    Vue pour renvoyer l'email de réinitialisation
    """
    permission_classes = [AllowAny]
    serializer_class = ResendResetEmailSerializer
    
    @extend_schema(
        summary="Renvoyer l'email de réinitialisation",
        description="Renvoie l'email de réinitialisation si un token valide existe, sinon en crée un nouveau",
        request=ResendResetEmailSerializer,
        responses={
            200: {"description": "Email renvoyé avec succès"},
            400: {"description": "Données invalides"}
        }
    )
    def post(self, request):
        serializer = ResendResetEmailSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
