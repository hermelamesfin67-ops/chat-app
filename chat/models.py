from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser,BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        phone_number=str(phone_number).strip()
        if not phone_number:
            raise ValueError("Phone number is required")
        if not phone_number.isdigit():
            raise ValueError("Phone number must contain only numbers")
        if len(phone_number) != 10:
            raise ValueError(f"Phone number must be 10 digits, you entered {len(phone_number)} digits")
        if not phone_number.startswith("09"):
            raise ValueError("Phone number must start with 09")
        phone_number='+251'+ phone_number[1:]
        if User is  None:
            raise ValueError('invalid username or password') 
        
        user = self.model(
            phone_number=phone_number,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("user", "User"),
    ]
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="user")
    phone_number=models.CharField(max_length=20, unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    bio = models.CharField(max_length=50, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD='phone_number'
    REQUIRED_FIELDS=['username']

    objects = UserManager()

    def __str__(self):
        return self.username


class Conversation(models.Model):
    participants = models.ManyToManyField( settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def other_user(self, current_user):
        return self.participants.exclude(id=current_user.id).first()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("sticker", "Sticker"),
        ("file", "File"),
    ]
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default="text")
    media = models.FileField( upload_to='message/',blank=True, null=True)

    class meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}:{self.text[:35]}"
