from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.UserRoles.ADMIN)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    class UserRoles(models.TextChoices):
        """Rôles natifs du système - utilisés pour référence et validation côté code"""
        ADMIN = "admin", "Administrateur"
        CUSTOMER = "customer", "Client"
        COLLABORATOR = "collaborator", "Collaborateur"
        SALES = "sales", "Commercial"
        INSTALLER = "installer", "Installateur"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = None
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    accept_invitation = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # Pas de choices pour permettre les rôles dynamiques créés via Role model
    role = models.CharField(max_length=50, default=UserRoles.COLLABORATOR)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.get_full_name() or self.email
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
    
    def is_native_role(self):
        """Vérifie si le rôle de l'utilisateur est un rôle natif du système"""
        return self.role in [choice[0] for choice in self.UserRoles.choices]
    
    def get_role_display(self):
        """Retourne le libellé du rôle (natif ou personnalisé)"""
        # Pour les rôles natifs, retourner le label défini
        for choice_value, choice_label in self.UserRoles.choices:
            if self.role == choice_value:
                return choice_label
        # Pour les rôles personnalisés, retourner le nom tel quel
        return self.role

class UserAccess(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    installation = models.BooleanField(default=False)
    offers = models.BooleanField(default=False)
    requests = models.BooleanField(default=False)
    administrative_procedures = models.BooleanField(default=False)

    def __str__(self):
        return f"Accès de {self.user.get_full_name() or self.user.email}"


class Role(models.Model):
    """Rôle dynamique définissable côté admin (non encore relié aux utilisateurs).

    Champs d'accès calqués sur UserAccess pour réutiliser même logique d'autorisations.
    """
    name = models.CharField(max_length=20, unique=True)
    installation = models.BooleanField(default=False)
    offers = models.BooleanField(default=False)
    requests = models.BooleanField(default=False)
    administrative_procedures = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ["name"]

    def __str__(self):
        return self.name




class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users_password_reset_token'
        verbose_name = 'Token de réinitialisation de mot de passe'
        verbose_name_plural = 'Tokens de réinitialisation de mot de passe'
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Vérifie si le token est encore valide"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.is_used = True
        self.save()
