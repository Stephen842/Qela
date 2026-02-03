from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
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

        extra_fields.setdefault('is_active', True)

        user = self.model(
            email=email,
            **extra_fields
        )
        if not password:
            raise ValueError('Password is required')
        user.set_password(password)  # Hash the password

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        

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
    is_staff = models.BooleanField(default=False)

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
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "Users"


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