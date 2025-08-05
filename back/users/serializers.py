from rest_framework import serializers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import secrets
import string
from .models import User, UserAccess


class UserAccessSerializer(serializers.ModelSerializer):
    """Serializer pour les droits d'accès des utilisateurs"""
    
    class Meta:
        model = UserAccess
        fields = ['installation', 'offers', 'requests', 'administrative_procedures']


class UserSerializer(serializers.ModelSerializer):
    """Serializer principal pour les utilisateurs"""
    access = UserAccessSerializer(source='useraccess', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'access', 'password']
        read_only_fields = ['id', 'is_staff', 'is_superuser']
        
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
        
    def send_welcome_email(self, user, password):
        """Envoie l'email de bienvenue avec le mot de passe"""
        try:
            subject = "Bienvenue chez EuropGreen Solar - Vos identifiants de connexion"
            
            # Contexte pour le template
            context = {
                'user': user,
                'password': password,
                'frontend_url': settings.FRONTEND_URL,
            }
            
            html_message = render_to_string('emails/welcome_user.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
    
    def create(self, validated_data):
        """Création d'un utilisateur avec génération automatique du mot de passe"""
        # Génération du mot de passe sécurisé
        password = self.generate_secure_password()
        
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
            UserAccess.objects.create(user=user)
        
        self.send_welcome_email(user, password)
        
        return user
    
    def update(self, instance, validated_data):
        """Mise à jour d'un utilisateur avec gestion des accès"""
        # Récupération de l'ancien rôle pour comparaison
        old_role = instance.role
        
        # Mise à jour des champs de base
        for attr, value in validated_data.items():
            if attr != 'password':
                setattr(instance, attr, value)
        
        # Définition des permissions selon le nouveau rôle
        self._set_user_permissions(instance)
        instance.save()
        
        new_role = instance.role
        
        # Si le nouveau rôle est client ou admin, supprime les accès existants
        if new_role in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            UserAccess.objects.filter(user=instance).delete()
        # Si l'ancien rôle était client/admin et le nouveau ne l'est pas, crée les accès
        elif old_role in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN] and new_role not in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            UserAccess.objects.get_or_create(user=instance)
        
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
        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(value)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def save(self, **kwargs):
        """Sauvegarde le nouveau mot de passe"""
        user = self.context.get('user')
        if user:
            user.set_password(self.validated_data['new_password'])
            user.save()
        return user


class UserAccessUpdateSerializer(serializers.ModelSerializer):
    """Serializer séparé pour la mise à jour des accès utilisateur"""
    
    class Meta:
        model = UserAccess
        fields = ['installation', 'offers', 'requests', 'administrative_procedures']
        
    def update(self, instance, validated_data):
        """Mise à jour des droits d'accès"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
