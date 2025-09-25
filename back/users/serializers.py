from rest_framework import serializers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import requests
import secrets
import string
from .models import User, UserAccess
from installations.models import Form as InstallationForm


class UserAccessSerializer(serializers.ModelSerializer):
    """Serializer pour les droits d'accès des utilisateurs"""
    
    class Meta:
        model = UserAccess
        fields = ['installation', 'offers', 'requests', 'administrative_procedures']

class UserSerializer(serializers.ModelSerializer):
    useraccess = UserAccessSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser', 'useraccess']
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'role']

class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer l'administration des utilisateurs"""
    useraccess = UserAccessSerializer()
    installations_count = serializers.SerializerMethodField(read_only=True)
    last_installation = serializers.SerializerMethodField(read_only=True)
    # password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'accept_invitation', 'is_active', 'is_staff', 'is_superuser', 'useraccess', 'installations_count', 'last_installation']
        read_only_fields = ['id', 'accept_invitation', 'is_staff', 'is_superuser']

    def get_installations_count(self, obj: User):
        """Nombre d'installations du client (uniquement pour les non-staff)."""
        try:
            if obj.is_staff:
                return 0
            return InstallationForm.objects.filter(client=obj).count()
        except Exception:
            return 0

    def get_last_installation(self, obj: User):
        """Dernière installation (id, status, installer) pour les non-staff."""
        try:
            if obj.is_staff:
                return None
            last_qs = (
                InstallationForm.objects
                .select_related('affected_user')
                .filter(client=obj)
                .order_by('-created_at')
            )
            last = last_qs.first()
            if not last:
                return None
            payload = { 'id': str(last.id), 'status': last.status }
            if last.affected_user_id and last.affected_user:
                payload['installer'] = {
                    'id': str(last.affected_user.id),
                    'first_name': last.affected_user.first_name,
                    'last_name': last.affected_user.last_name,
                }
            return payload
        except Exception:
            return None
        
    def _set_user_permissions(self, user):
        """Définit les permissions selon le rôle"""
        if user.role == User.UserRoles.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        elif user.role == User.UserRoles.CUSTOMER:
            user.is_staff = False
            user.is_superuser = False
        else:
            # Autres rôles (EMPLOYEE, INSTALLER, SECRETARY)
            user.is_staff = True
            user.is_superuser = False
        
    def generate_secure_password(self):
        """Génère un mot de passe sécurisé"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        return password
    
    def send_welcome_email_mailgun(self, user, password):
        """Envoi via Mailgun API"""
        try:
            # Contexte pour le template (même que votre version SMTP)
            context = {
                'user': user,
                'password': password,
                'frontend_url': settings.FRONTEND_URL,
            }
            
            # Utiliser votre template existant
            html_message = render_to_string('emails/user/welcome_user.html', context)
            plain_message = strip_tags(html_message)
            
            response = requests.post(
                f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
                auth=("api", settings.MAILGUN_API_KEY),
                data={
                    "from": f"Europ'Green Solar <noreply@{settings.MAILGUN_DOMAIN}>",
                    "to": user.email,
                    "subject": "Bienvenue chez EuropGreen Solar - Vos identifiants de connexion",
                    "text": plain_message,
                    "html": html_message
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Email envoyé avec succès"
            else:
                return False, f"Erreur Mailgun: {response.text}"
                
        except Exception as e:
            return False, f"Erreur Mailgun: {str(e)}"
    
    def send_welcome_email_smtp(self, user, password):
        """Envoi via SMTP (votre méthode actuelle)"""
        try:
            subject = "Bienvenue chez EuropGreen Solar - Vos identifiants de connexion"
            
            context = {
                'user': user,
                'password': password,
                'frontend_url': settings.FRONTEND_URL,
            }

            html_message = render_to_string('emails/user/welcome_user.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=f"Europ'Green Solar<{settings.DEFAULT_FROM_EMAIL}>",
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True, "Email envoyé avec succès"
            
        except Exception as e:
            return False, f"Erreur SMTP: {str(e)}"
    
    def send_welcome_email(self, user, password):
        """
        Méthode principale qui choisit entre Mailgun et SMTP
        Retourne (success, message, password_for_response)
        """
        # Vérifier si Mailgun est configuré
        mailgun_configured = (
            hasattr(settings, 'MAILGUN_API_KEY') and 
            hasattr(settings, 'MAILGUN_DOMAIN') and 
            settings.MAILGUN_API_KEY and 
            settings.MAILGUN_DOMAIN
        )
        
        if mailgun_configured:
            success, message = self.send_welcome_email_mailgun(user, password)
            if success:
                return True, message, None
            else:
                # Mailgun a échoué, essayer SMTP en fallback
                print(f"Mailgun échoué: {message}, tentative SMTP...")
        
        # Utiliser SMTP (soit par choix, soit en fallback)
        success, message = self.send_welcome_email_smtp(user, password)
        
        if success:
            return True, message, None
        else:
            # SMTP aussi a échoué, retourner le mot de passe
            return False, message, password
        
    def create(self, validated_data):
        """Création d'un utilisateur avec génération automatique du mot de passe"""
        # Génération du mot de passe sécurisé
        password = self.generate_secure_password()
        access = validated_data.pop('useraccess')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data.get('role', User.UserRoles.EMPLOYEE),
            password=password
        )
        
        # Définition des permissions selon le rôle
        self._set_user_permissions(user)
        user.save()
        
        # Création des accès par défaut uniquement pour les utilisateurs qui ne sont pas client ou admin
        if user.role not in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            UserAccess.objects.create(user=user, **access)

        email_success, email_message, fallback_password = self.send_welcome_email(user, password)
        
        if not email_success:
            # L'email n'a pas pu être envoyé, mais l'utilisateur est créé
            # Lever une exception avec les détails
            error_message = {
                "detail": "Compte créé avec succès, mais l'email n'a pas pu être envoyé.",
                "message": f"Le compte de {user.email} a été créé mais l'email de bienvenue n'a pas pu être envoyé. Mot de passe temporaire : {fallback_password}"
            }
            
            raise serializers.ValidationError(error_message)
        
        return user
    
    def update(self, instance, validated_data):
        """Mise à jour d'un utilisateur avec gestion des accès"""
        # Récupération de l'ancien rôle pour comparaison
        old_role = instance.role
        access = validated_data.pop('useraccess', None)
        
        # Mise à jour des champs de base
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Définition des permissions selon le nouveau rôle
        self._set_user_permissions(instance)
        instance.save()
        
        new_role = instance.role
        
        # Si le nouveau rôle est client ou admin, supprime les accès existants
        if new_role in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            UserAccess.objects.filter(user=instance).delete()
        # Si l'ancien rôle était client/admin et le nouveau ne l'est pas, crée les accès
        user_access, created = UserAccess.objects.get_or_create(user=instance)
        if access:
            print('access', access)
            # Mise à jour des accès existants
            for attr, value in access.items():
                setattr(user_access, attr, value)
            user_access.save()
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    
    def validate_old_password(self, value):
        """Valide l'ancien mot de passe"""
        user = self.context.get('user')
        if not user or not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Valide le nouveau mot de passe"""
        # from django.contrib.auth.password_validation import validate_password
        # try:
        #     validate_password(value)
        # except Exception as e:
        #     raise serializers.ValidationError(str(e))
        return value
    
    def save(self, **kwargs):
        """Sauvegarde le nouveau mot de passe"""
        user = self.context.get('user')
        if user:
            user.set_password(self.validated_data['new_password'])
            user.save()
        return user
    