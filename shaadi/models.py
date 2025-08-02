# shaadi/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from datetime import date

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    
    RELIGION_CHOICES = [
        ('M', _('Muslim')),
        ('C', _('Christian')),
        ('H', _('Hindu')),
        ('S', _('Sikh')),
        ('O', _('Other')),
    ]
    
    username = models.CharField(_('Username'), max_length=150, unique=True)
    email = models.EmailField(_('Email Address'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True)
    
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    # Custom fields
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(_('Date of Birth'), blank=True, null=True)
    religion = models.CharField(max_length=1, choices=RELIGION_CHOICES, blank=True, null=True)
    phone = models.CharField(_('Phone Number'), max_length=15, blank=True)
    address = models.TextField(_('Address'), blank=True)
    profile_picture = models.ImageField(_('Profile Picture'), upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(_('About Me'), blank=True)
    profession = models.CharField(_('Profession'), max_length=100, blank=True)
    education = models.CharField(_('Education'), max_length=100, blank=True)
    
    # Partner preferences
    preferred_age_min = models.PositiveSmallIntegerField(_('Minimum Preferred Age'), blank=True, null=True)
    preferred_age_max = models.PositiveSmallIntegerField(_('Maximum Preferred Age'), blank=True, null=True)
    preferred_religion = models.CharField(max_length=1, choices=RELIGION_CHOICES, blank=True, null=True)
    
    # Django auth fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.username
    
    # shaadi/models.py
class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"