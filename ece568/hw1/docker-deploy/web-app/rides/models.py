from contextlib import nullcontext
from email.policy import default
from django.db import models
from django.db.models.fields import BooleanField, CharField, IntegerField
from django.http import request
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class OrderInfo(models.Model):
    owner=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    username=models.CharField(max_length=50,default='',blank=True)
    userid=models.CharField(max_length=50,default='',blank=True)
    user_email=models.CharField(max_length=50, default="1148201178@qq.com")
    driver_name=models.CharField(max_length=50,default='')
    plate_num=models.CharField(max_length=20,default='')
    dest_addr=models.TextField(default='')
    arrival_date=models.DateTimeField(default=timezone.now)
    passenger_num=models.PositiveSmallIntegerField(default=1)
    vehicle_type=models.CharField(max_length=30,blank=True)
    special_info=models.TextField(blank=True)
    is_shared=models.BooleanField(default=False)
    shared_seats=models.PositiveSmallIntegerField(default=0)
    #sharer_name=models.CharField(max_length=50, default=NULL)
    sharer_num=models.PositiveSmallIntegerField(default=0)
    status=models.CharField(max_length=10, default='open')
    

    def __str__(self):
        return self.dest_addr
        #return self.rideowner.user.username
    
    def get_absolute_url(self):
        return reverse('orderlist', kwargs={'pk': self.pk})



class RideSharer(models.Model):
    #每个sharer属于一个order                                                
    sharer=models.ForeignKey(User, on_delete=models.CASCADE)
    sharer_email=models.CharField(max_length=50, default="1148201178@qq.com")
    ride_order=models.ForeignKey(OrderInfo, on_delete=models.CASCADE)

 

class RideOwner(models.Model):
    orderinfo=models.OneToOneField(OrderInfo, on_delete=models.CASCADE)
    username=models.CharField(max_length=50,default='')
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    owner_email=models.CharField(max_length=50, default="1148201178@qq.com")
    #ride_order=models.OneToOneField(OrderInfo, on_delete=models.CASCADE)
