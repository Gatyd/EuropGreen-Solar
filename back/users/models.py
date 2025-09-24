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
        EMPLOYEE = "employee", "Employee"
        INSTALLER = "installer", "Installer"
        SECRETARY = "secretary", "Secretary"
        REGIONAL_MANAGER = "regional_manager", "Regional Manager"
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Administrateur"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = None
    is_active = models.BooleanField(default=True)
    accept_invitation = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=17, choices=UserRoles.choices, default=UserRoles.EMPLOYEE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class UserAccess(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    installation = models.BooleanField(default=False)
    offers = models.BooleanField(default=False)
    requests = models.BooleanField(default=False)
    administrative_procedures = models.BooleanField(default=False)


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
