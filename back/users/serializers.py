from rest_framework import serializers
from django.conf import settings
import secrets
import string
from .models import User, UserAccess, Role
from installations.models import Form as InstallationForm
from EuropGreenSolar.email_utils import send_mail


class UserAccessSerializer(serializers.ModelSerializer):
    """Serializer pour les droits d'accès des utilisateurs"""
    
    class Meta:
        model = UserAccess
        fields = ['installation', 'offers', 'requests', 'administrative_procedures']


class UserSerializer(serializers.ModelSerializer):
    useraccess = UserAccessSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser', 'accept_invitation', 'useraccess']
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'role', 'accept_invitation']

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
        """Dernière installation (id, status, installer, commissions) pour les non-staff."""
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
            payload = { 
                'id': str(last.id), 
                'status': last.status,
                'commission_amount': float(last.commission_amount) if last.commission_amount else 0,
                'commission_paid': last.commission_paid,
                'sales_commission_amount': float(last.sales_commission_amount) if last.sales_commission_amount else 0,
                'sales_commission_paid': last.sales_commission_paid,
            }
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
        """Génère un mot de passe sécurisé sans caractères ambigus
        
        Caractères exclus pour éviter toute confusion visuelle :
        - l (L minuscule), I (i majuscule), 1 (un) : trop similaires
        - O (o majuscule), 0 (zéro) : trop similaires
        - S, 5 : peuvent se confondre selon la police
        - Z, 2 : peuvent se confondre selon la police
        - B, 8 : peuvent se confondre dans certains cas
        """
        # Ensemble de base
        letters = string.ascii_letters  # a-z, A-Z
        digits = string.digits          # 0-9
        special = "!@#$%^&*"
        
        # Retirer les caractères ambigus
        ambiguous_chars = "lIO01SZ2B8"  # l, I, O, 0, 1, S, Z, 2, B, 8
        
        # Construire l'alphabet filtré
        safe_letters = ''.join(c for c in letters if c not in ambiguous_chars)
        safe_digits = ''.join(c for c in digits if c not in ambiguous_chars)
        safe_alphabet = safe_letters + safe_digits + special
        
        # Générer le mot de passe (12 caractères)
        password = ''.join(secrets.choice(safe_alphabet) for _ in range(12))
        return password
        
    def create(self, validated_data):
        """
        Création d'un utilisateur avec génération automatique du mot de passe.
        L'email de bienvenue est envoyé en arrière-plan, le retour est immédiat.
        """
        # Génération du mot de passe sécurisé
        password = self.generate_secure_password()
        access = validated_data.pop('useraccess')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', User.UserRoles.INSTALLER),
            password=password
        )
        
        # Définition des permissions selon le rôle
        self._set_user_permissions(user)
        user.save()
        
        # Création des accès par défaut uniquement pour les utilisateurs qui ne sont pas client ou admin
        if user.role not in [User.UserRoles.CUSTOMER, User.UserRoles.ADMIN]:
            UserAccess.objects.create(user=user, **access)

        # Préparer les données d'accès pour l'email (sérialisation compatible)
        try:
            user_access = user.useraccess
            access_data = {
                'installation': user_access.installation,
                'offers': user_access.offers,
                'requests': user_access.requests,
                'administrative_procedures': user_access.administrative_procedures,
            }
        except UserAccess.DoesNotExist:
            access_data = None

        # Envoi de l'email de bienvenue en arrière-plan avec les identifiants
        # L'email contient le mot de passe donc n'est PAS enregistré dans l'historique
        email_context = {
            'user': user,
            'password': password,
            'frontend_url': settings.FRONTEND_URL,
            'role_display': user.get_role_display(),  # Pré-calculer pour éviter la perte lors de la sérialisation
        }
        if access_data:
            email_context['user_access'] = access_data
        
        send_mail(
            template='emails/user/welcome_user.html',
            context=email_context,
            subject="Bienvenue chez EuropGreen Solar - Vos identifiants de connexion",
            to=user.email,
            save_to_log=False,  # Ne pas enregistrer car contient le mot de passe
            async_send=True,     # Envoi asynchrone via Celery
        )
        
        # L'utilisateur est créé avec succès, l'email sera envoyé en arrière-plan
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


class RoleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Role
		fields = [
			'id', 'name', 'installation', 'offers', 'requests', 'administrative_procedures', 'created_at', 'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at']
    