from django.db import models
from django.db.models.fields import CharField
from django.utils import timezone
from django.contrib.auth.models import User

class RideOwnerInfo(models.Model):
    username = models.CharField()
    destaddr = models.TextField()
