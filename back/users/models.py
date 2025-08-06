from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid

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
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    class UserRoles(models.TextChoices):
        EMPLOYEE = "employee", "Employee"
        INSTALLER = "installer", "Installer"
        SECRETARY = "secretary", "Secretary"
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
    role = models.CharField(max_length=10, choices=UserRoles.choices, default=UserRoles.EMPLOYEE)

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
