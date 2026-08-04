from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def other_user(self, current_user):
        return self.participants.exclude(id=current_user.id).first()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
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
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)

    class meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}:{self.content[:35]}"
