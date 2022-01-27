from cProfile import Profile
from django.db.models.signals import post_save
from django.contrib.auth.models import User
#receiver to receive the signal and create the driver profile
from django.dispatch import receiver
from .models import DriverProfile

@receiver(post_save, sender=User)
def create_driverprofile(sender, instance, created, **kwargs):
    if created:
        DriverProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_driverprofile(sender, instance, **kwargs):
    instance.driverprofile.save()