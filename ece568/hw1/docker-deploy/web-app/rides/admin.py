from django.contrib import admin

# Register your models here.
from .models import OrderInfo
from .models import RideOwner, RideSharer
admin.site.register(OrderInfo)
admin.site.register(RideOwner)