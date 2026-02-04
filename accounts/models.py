from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class UsersManager(BaseUserManager):
    '''
    Custom manager for User.
    '''
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email=self.normalize_email(email).lower()

        # Regular users start inactive and unverified
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_verified", False)
        extra_fields.setdefault("is_platform_admin", False)

        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password) # Hash the password
        else:
            # Required for OAuth users
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_platform_admin", True)
        

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    '''
    Custom User model for Future Of Work.
    '''
    name = models.CharField(max_length=80)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now, db_index=True)
    
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Global platform-level admin (organization-owned)
    is_platform_admin = models.BooleanField(default=False)

    # Temporary email storage for pending email updates
    _new_email = models.EmailField(null=True, blank=True)
    email_verification_pending = models.BooleanField(default=False)

    account_updated_at = models.DateTimeField(null=True, blank=True)

    is_deactivated = models.BooleanField(default=False)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    # Track last activity for automatic deletion
    last_activity = models.DateTimeField(default=timezone.now)

    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']

    def save(self, *args, **kwargs):
        '''Ensure username and email are stored in lowercase'''
        self.email = self.email.lower()
        self.username = self.username.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        '''Return the user's full name'''
        return self.name

    def get_short_name(self):
        '''Return the short name (username in this case)'''
        return self.username
    
    # Utility method to check if account can be deleted
    def can_delete_account(self):
        if self.is_deactivated and self.deactivated_at:
            return timezone.now() >= self.deactivated_at + timedelta(days=30)
        return False
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_platform_admin']),
        ]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,  related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    country = CountryField(blank=False, blank_label='Select Country',)

    # Use PhoneNumberField for validation
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        indexes = [
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f'{self.user.username} Profile'
    

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField()

    device_type = models.CharField(max_length=50, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=50, blank=True, null=True)

    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['ip_address']),
            models.Index(fields=["last_active"]),
        ]
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.user.email} - {self.browser or 'Unknown Browser'}"


class IPActivity(models.Model):
    ip_address = models.GenericIPAddressField(db_index=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)

    request_count = models.PositiveIntegerField(default=1)
    failed_attempts = models.PositiveIntegerField(default=0)

    last_seen = models.DateTimeField(auto_now=True)
    first_seen = models.DateTimeField(auto_now_add=True)

    is_suspicious = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ip_address', 'endpoint', 'method')
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_suspicious']),
            models.Index(fields=['last_seen']),
        ]


class BlacklistedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['ip_address']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        status = 'active' if self.is_active else 'inactive'
        return f'{self.ip_address} ({status})'