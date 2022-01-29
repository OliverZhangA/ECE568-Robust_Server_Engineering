from contextvars import Context
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import OrderInfo, RideOwner, RideSharer
from users.models import DriverProfile
from .forms import OrderInfoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.views import driverform
from django.db.models import Q


def home(request):
    return render(request, 'rides/home.html')

def userhome(request):
    return render(request, 'rides/userhome.html')

def sharer(request):
    return render(request, 'rides/sharer.html')

def driver(request):
    ride_driver = DriverProfile.objects.filter(user=request.user).first()
    if ride_driver.plate_num == '':
        return redirect(driverform)
        #return render(request, 'rides/driver_register.html')
    else:
        return redirect('takeorders')
        #return render(request, 'rides/driver.html')
        #return redirect()

class OrderList(ListView):
    model = OrderInfo
    template_name = 'rides/orderlist.html'
    context_object_name = 'orders'
    ordering = ['-arrival_date']
    def get_queryset(self):
        #return OrderInfo.objects.filter(rideowner__user=self.request.user).exclude(status='complete').order_by('arrival_date')
        return OrderInfo.objects.filter(owner=self.request.user).exclude(status='complete').order_by('arrival_date')
        #return OrderInfo.objects.filter(userid=self.request.user.id).exclude(status='complete').order_by('arrival_date')

class OrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/orderdetail.html'
    # template_name = 'rides/orderdetail.html'
    # context_object_name = 'order'

class OrderCreate(LoginRequiredMixin, CreateView):
    model = OrderInfo
    template_name = 'rides/order_form.html'
    fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        #form.save()
        return super().form_valid(form)


class OrderUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OrderInfo
    template_name = 'rides/order_update.html'
    fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']

    def form_valid(self, form):
        if(form.instance.status == 'confirmed'):
            return HttpResponse('no permission')        
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        order = self.get_object()
        if self.request.user == order.owner:
            return True
        return False
    
class ShareOrderCreate(LoginRequiredMixin, CreateView):
    model = RideSharer
    template_name = 'rides/order_form.html'
    fields = ['dest_addr', 'arrival_early', 'arrival_late', 'passenger_num']

    def form_valid(self, form):
        form.instance.sharer = self.request.user
        #form.save()
        return super().form_valid(form)

class ShareList(ListView):
    model = OrderInfo
    template_name = 'rides/shareorderlist.html'
    context_object_name = 'orders'
    ordering = ['-arrival_date']
    def get_queryset(self):
        sharer = self.request.user.ridesharer_set.last()
        #target = RideSharer.objects.get(sharer=self.request.user)
        return OrderInfo.objects.filter(is_shared=True, dest_addr=sharer.dest_addr, arrival_date__lte=sharer.arrival_late, arrival_date__gte=sharer.arrival_early)#, shared_seats__gte=sharer.passenger_num)

class ShareOrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/shareorderdetail.html'
    # template_name = 'rides/orderdetail.html'
    # context_object_name = 'order'

class DriverOrderList(ListView):
    model = OrderInfo
    template_name = 'rides/driverorderlist.html'
    context_object_name = 'orders'
    ordering = ['-arrival_date']
    def get_queryset(self):
        driver = self.request.user.driverprofile
        return OrderInfo.objects.filter(plate_num=driver.plate_num, status='confirmed')

class DriverOrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/driverorderdetail.html'

def joinconfirm(request, order_id):
    sharer_toadd = request.user.ridesharer_set.last()
    order_toadd = OrderInfo.objects.filter(pk=order_id).first()
    order_toadd.shared_seats = order_toadd.shared_seats - sharer_toadd.passenger_num
    #order_toadd.save()
    sharer_toadd.ride_order = order_toadd
    
    #sharer_toadd.save()
    return HttpResponse('confirm success')


class DriverList(ListView):
    model = OrderInfo
    template_name = 'rides/driver.html'
    context_object_name = 'orders'
    ordering = ['-arrival_date']
    def get_queryset(self):
        driver = self.request.user.driverprofile
        return OrderInfo.objects.filter(Q(vehicle_type=driver.vehicle_type)|Q(vehicle_type=''), Q(special_info=driver.special_info)|Q(special_info=''), status='open', passenger_num__lte=driver.vehicle_capacity)

class DriverConfirmDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/driverdetail.html'

def DriverConfirm(request, order_id):
    driver = request.user.driverprofile
    order = OrderInfo.objects.filter(pk=order_id).first()
    order.shared_seats = driver.vehicle_capacity - order.passenger_num
    order.status = 'confirmed'
    order.driver_name = driver.user.username
    order.plate_num = driver.plate_num
    order.vehicle_type = driver.vehicle_type
    order.save()
    return HttpResponse('confirm success')

def DriverComplete(request, order_id):
    driver = request.user.driverprofile
    order = OrderInfo.objects.filter(pk=order_id).first()
    order.status = 'complete'
    order.save()
    return HttpResponse('complete success')

