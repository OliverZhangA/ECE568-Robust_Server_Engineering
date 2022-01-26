#from asyncio.windows_events import NULL
from django.db import models
from django.db.models.fields import BooleanField, CharField, IntegerField
from django.utils import timezone
from django.contrib.auth.models import User

class OrderInfo(models.Model):
    username=models.CharField(max_length=50)
    user_email=models.CharField(max_length=50, default="1148201178@qq.com")
    driver_name=models.CharField(max_length=50)
    plate_num=models.CharField(max_length=20)
    dest_addr=models.TextField()
    arrival_date=models.DateTimeField(auto_now_add=True)
    passenger_num=models.PositiveSmallIntegerField(default=1)
    vehicle_type=models.CharField(max_length=30)
    special_info=models.TextField()
    is_shared=models.BooleanField(default=False)
    shared_seats=models.PositiveSmallIntegerField(default=0)
    #sharer_name=models.CharField(max_length=50, default=NULL)
    sharer_num=models.PositiveSmallIntegerField(default=0)
    status=models.CharField(max_length=10, default='open')


#class RideSharer(models.Model):
    #每个sharer属于一个order                                                
    #sharer=
    #email=
    #orderinfo=

# class RideOwner(models.Model):
#     owner=models.CharField(max_length=50)
#     owner_email=models.CharField(max_length=50, default="1148201178@qq.com")
#     ride_order=models.OnetoOne
