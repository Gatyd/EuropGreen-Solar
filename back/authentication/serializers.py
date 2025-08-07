from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from users.models import User, PasswordResetToken

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only = True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError({
                "Connexion impossible": "Identifiants invalides"
            })
        
        data['user'] = user
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Normalise l'email"""
        return value.lower().strip()
    
    def send_reset_email(self, user, token):
        """Envoie l'email de réinitialisation de mot de passe"""
        try:
            subject = "Réinitialisation de votre mot de passe - EuropGreen Solar"
            
            # URL du frontend pour la réinitialisation
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'expires_at': token.expires_at,
                'frontend_url': settings.FRONTEND_URL,
            }
            
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de réinitialisation: {e}")
            return False
    
    def create_reset_token(self, user):
        """Crée un nouveau token de réinitialisation"""
        # Invalider tous les anciens tokens non utilisés pour cet utilisateur
        PasswordResetToken.objects.filter(
            user=user, 
            is_used=False, 
            expires_at__gt=timezone.now()
        ).update(is_used=True)
        
        # Créer un nouveau token
        token = PasswordResetToken.objects.create(user=user)
        return token
    
    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            token = self.create_reset_token(user)
            email_sent = self.send_reset_email(user, token)
            
            return {
                'success': True, 
                'message': 'Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation.',
                'email_sent': email_sent
            }
        except User.DoesNotExist:
            # Ne pas révéler que l'email n'existe pas pour des raisons de sécurité
            return {
                'success': True, 
                'message': 'Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation.',
                'email_sent': False
            }


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, data):
        """Valide que les mots de passe correspondent"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Les mots de passe ne correspondent pas.'
            })
        return data
    
    def validate_token(self, value):
        """Valide le token de réinitialisation"""
        try:
            token = PasswordResetToken.objects.get(token=value)
            if not token.is_valid():
                raise serializers.ValidationError('Ce lien de réinitialisation a expiré ou a déjà été utilisé.')
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Token de réinitialisation invalide.')
    
    def save(self):
        token_value = self.validated_data['token']
        new_password = self.validated_data['new_password']
        
        try:
            token = PasswordResetToken.objects.get(token=token_value)
            user = token.user
            
            # Changer le mot de passe
            user.set_password(new_password)
            user.save()
            
            # Marquer le token comme utilisé
            token.mark_as_used()
            
            return {
                'success': True,
                'message': 'Votre mot de passe a été réinitialisé avec succès.'
            }
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({'token': 'Token invalide.'})


class ResendResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Normalise l'email"""
        return value.lower().strip()
    
    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Vérifier s'il y a déjà un token valide
            existing_token = PasswordResetToken.objects.filter(
                user=user, 
                is_used=False, 
                expires_at__gt=timezone.now()
            ).first()
            
            if existing_token:
                # Renvoyer l'email avec le token existant
                forgot_serializer = ForgotPasswordSerializer()
                email_sent = forgot_serializer.send_reset_email(user, existing_token)
            else:
                # Créer un nouveau token et envoyer l'email
                forgot_serializer = ForgotPasswordSerializer()
                token = forgot_serializer.create_reset_token(user)
                email_sent = forgot_serializer.send_reset_email(user, token)
            
            return {
                'success': True,
                'message': 'Email de réinitialisation renvoyé avec succès.',
                'email_sent': email_sent
            }
        except User.DoesNotExist:
            return {
                'success': True,
                'message': 'Si cette adresse email existe dans notre système, l\'email a été renvoyé.',
                'email_sent': False
            }
