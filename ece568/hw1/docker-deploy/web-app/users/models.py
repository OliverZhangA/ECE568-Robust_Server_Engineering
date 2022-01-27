from email.policy import default
from lib2to3.pgen2 import driver
from pickle import FALSE, TRUE
from pyexpat import model
from typing import Text
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
from django.db.models.fields import CharField, IntegerField, TextField

# Create your models here.
class DriverProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='driverprofile')
    image = models.ImageField(default='default.gif', upload_to='profile_pics')
    vehicle_type = CharField(max_length=50,blank=False)
    vehicle_capacity = IntegerField(default=1)
    plate_num = CharField(max_length=7,blank=False)
    license_num = CharField(max_length=12,blank=False)
    special_info = TextField(max_length=200,blank=TRUE)
    def __str__(self):
        return f'{self.user.username} Profile'