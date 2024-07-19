from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import string


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=5))


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=5, default=generate_verification_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 180


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class UserProfileImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='profile_images/')
    created = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name='chats')

    def __str__(self):
        return f"Chat id {self.id} with participants {', '.join([user.username for user in self.participants.all()])}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
