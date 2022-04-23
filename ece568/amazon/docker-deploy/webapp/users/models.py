from email.policy import default
from lib2to3.pgen2 import driver
from pickle import FALSE, TRUE
from pyexpat import model
from typing import Text
from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
from django.db.models.fields import CharField, IntegerField, TextField
from django.utils import timezone

# VEHICLE_TYPE_CHOICES = [
#         ('Sedan', 'Sedan'),
#         ('Coupe', 'Gold'),
#         ('SUV', 'SUV'),
#         ('Minivan', 'Minivan'),
#     ]

# Create your models here.
class DriverProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='driverprofile')
    # name = CharField(max_length=50,blank=False,null=True)
    # ID_num = CharField(max_length=20,blank=False,null=True)
    # DOB = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default='default.gif', upload_to='profile_pics')
    # vehicle_type = CharField(max_length=50,choices=VEHICLE_TYPE_CHOICES,blank=False)
    # vehicle_capacity = IntegerField(default=0,blank=False)
    # plate_num = CharField(max_length=7,blank=False)
    # license_num = CharField(max_length=12,blank=False)
    # special_info = TextField(max_length=200,blank=TRUE)
    UPS_account = models.CharField(default = "", max_length=100, blank=True, null=True)
    dest_x = models.IntegerField(default=0, blank=True, null=False)
    dest_y = models.IntegerField(default=0, blank=True, null=False)
    cardnum = models.CharField(default = "", max_length=100, blank=True, null=True)
    seccode = models.CharField(default = "000", max_length=3, blank=True, null=True)
    valid_date = models.CharField(default = "12/25", max_length=5, blank=True, null=True)
    def __str__(self):
        return f'{self.user.username} Profile'