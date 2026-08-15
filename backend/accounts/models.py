import uuid
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from core.choices import UserRole, UserStatus, AuditAction
from core.models import Barangay


class UserManager(DjangoUserManager):
    """
    Extends Django's default UserManager so `python manage.py createsuperuser`
    (which only ever prompts for username/email/password) doesn't try to save
    role='' — which would fail the users_role_valid CHECK constraint. Regular
    account creation through the API always sets role/status explicitly via
    UserAdminSerializer, so this only affects the createsuperuser path.
    """
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', UserRole.BARANGAY_SECRETARY)
        extra_fields.setdefault('status', UserStatus.ACTIVE)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ImageField(upload_to='profile_avatars/', blank=True, null=True)
    role = models.CharField(max_length=30, choices=UserRole.choices)
    barangay = models.ForeignKey(
        Barangay,
        on_delete=models.PROTECT,
        related_name='users',
        null=True,
        blank=True,  # nullable: MDRRMO Officer is municipal-level, not tied to one barangay
    )
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE)
    assigned_purok = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Purok this user is responsible for. Currently only meaningful for Barangay Healthworkers, '
                   'whose Vulnerability_Indicators edit access is restricted to households in this purok.',
    )

    # Required overrides so this custom user model doesn't clash with
    # Django's default auth.User reverse accessors for groups/permissions.
    groups = models.ManyToManyField(Group, related_name='safealert_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='safealert_user_set', blank=True)

    objects = UserManager()

    class Meta:
        db_table = 'users'
        constraints = [
            models.CheckConstraint(condition=models.Q(role__in=UserRole.values), name='users_role_valid'),
            models.CheckConstraint(condition=models.Q(status__in=UserStatus.values), name='users_status_valid'),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"


class UserAddress(models.Model):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=150)
    sitio = models.CharField(max_length=100, blank=True, null=True)
    barangay = models.CharField(max_length=100)  # free-text per schema, not FK to core.Barangay
    municipality = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    address_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'user_addresses'

    def __str__(self):
        return f"{self.street}, {self.barangay} ({self.address_type or 'N/A'})"


class AuditLog(models.Model):
    """
    Lives in accounts (not core) because it FKs to User, while User itself
    FKs to core.Barangay — putting AuditLog in core would create a circular
    app dependency (core -> accounts -> core).
    """
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=AuditAction.choices)
    table_affected = models.CharField(max_length=100, blank=True, null=True)
    record_id = models.UUIDField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        constraints = [
            models.CheckConstraint(condition=models.Q(action__in=AuditAction.values), name='audit_logs_action_valid'),
        ]
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.user} - {self.action} @ {self.performed_at}"
