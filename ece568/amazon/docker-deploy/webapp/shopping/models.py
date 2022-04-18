from itertools import product
from tkinter import CASCADE
from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

#catalog for different kinds of products
class catalog(models.Model):
    cate_name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return str(self.cate_name)

#initialize a series of warehouses
class warehouse(models.Model):
    #need to get warehouse id??
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

class commodity(models.Model):
    commodity_name = models.CharField(max_length=100, null=False, blank=False)
    commodity_amt = models.IntegerField(default=0)
    commodity_price = models.FloatField(default=0)
    commodity_catalog = models.ForeignKey(catalog, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.commodity_name)

class package_info(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    from_wh = models.ForeignKey(warehouse, on_delete=models.SET_NULL, null=True)
    dest_x = models.IntegerField(default=0, blank=False, null=False)
    dest_y = models.IntegerField(default=0, blank=False, null=False)
    package_job_time = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, blank=False, null=False)
    ups_account = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return "<" + str(self.from_wh) + ", " + self.status + ">"

    def show_order(self):
        order_detail="order has been placed with following items:\n"
        for order in self.orders.all():
            order_detail+="+ %s*%s\n" % (str(order.commodity), str(order.commodity_amt))
        return order_detail

class order(models.Model):
    #owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    #order_time
    order_time = models.DateTimeField(default=now)
    #commodity
    commodity = models.ForeignKey(commodity, on_delete=models.CASCADE, null=True)
    commodity_amt = models.IntegerField(default=1)
    #package status??
    package_info = models.ForeignKey(package_info, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return "order time:" + str(self.order_time) + ", commodity:" + str(commodity) + "*" + str(self.commodity_amt) + "in package:" + str(package_info)



    
