from cProfile import Profile
from django.db.models.signals import post_save
from django.contrib.auth.models import User
#receiver to receive the signal and create the driver profile
from django.dispatch import receiver
from django.http import request
from .models import OrderInfo
from .models import RideOwner

@receiver(post_save, sender=OrderInfo)
def create_orderinfo(sender, instance, created, **kwargs):
    if created:
        RideOwner.objects.create(orderinfo=instance)

@receiver(post_save, sender=OrderInfo)
def save_driverprofile(sender, instance, **kwargs):
    instance.rideowner.save()