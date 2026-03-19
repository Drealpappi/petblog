import email
from email.mime import message
from unicodedata import name

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# 1. The Profile Model
class Profile(models.Model):
    USER_ROLES = (
        ('AUTHOR', 'AUTHOR'),
        ('READER', 'READER')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='READER')
    is_author = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role == 'AUTHOR':
            self.is_author = True
        else:
            self.is_author = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"