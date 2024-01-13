from django.db import models

# Create your models here.

from django.db import models


class StoredImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    identifier = models.CharField(max_length=50, unique=True)
    path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class FrontendEvent(models.Model):
    event_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
