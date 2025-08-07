from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from django.conf import settings
from .serializers import LoginSerializer
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
        print("Tentative de rafraîchissement du token...")
        refresh_token = get_refresh_token_from_cookie(request)
        if not refresh_token:
            print("Refresh token non fourni.")
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
