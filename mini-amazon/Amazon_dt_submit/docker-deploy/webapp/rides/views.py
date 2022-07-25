from contextvars import Context
from sre_constants import SUCCESS
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import OrderInfo, RideOwner, RideSharer
from users.models import DriverProfile
from .forms import OrderInfoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.views import driverform
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import Settings, settings


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
        return redirect('driver-home')
        #return render(request, 'rides/driver.html')

def driverhome(request):
    return render(request, 'rides/driverhome.html')

class OrderList(ListView):
    model = OrderInfo
    template_name = 'rides/orderlist.html'
    context_object_name = 'orders'
    ordering = ['arrival_date']
    def get_queryset(self):
        #return OrderInfo.objects.filter(rideowner__user=self.request.user).exclude(status='complete').order_by('arrival_date')
        return OrderInfo.objects.filter(owner=self.request.user).exclude(status='complete').order_by('arrival_date')
        #return OrderInfo.objects.filter(userid=self.request.user.id).exclude(status='complete').order_by('arrival_date')

class OrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/orderdetail.html'
    # template_name = 'rides/orderdetail.html'
    # context_object_name = 'order'

class OrderDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = OrderInfo
    template_name = 'rides/order_confirm_delete.html'
    success_url = '/rides/rideuser/ridehistory'

    def test_func(self):
        order = self.get_object()
        if self.request.user == order.owner:
            return True
        return False

class OrderCreate(LoginRequiredMixin, CreateView):
    model = OrderInfo
    template_name = 'rides/order_form.html'
    fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.total_num = form.cleaned_data.get('passenger_num') + form.instance.sharer_num
        #form.instance.shared_seats = -form.passenger_num
        #form.save()
        return super().form_valid(form)


class OrderUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OrderInfo
    template_name = 'rides/order_update.html'
    fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']

    #if(form.instance.total_num > )
    def form_valid(self, form):
        if(form.instance.ridesharer_set != [] and form.cleaned_data.get('is_shared') == False):
            return HttpResponse('no permission to edit, can not kick out existing sharers, please be kind!')
        if(form.instance.ridesharer_set != [] and form.cleaned_data.get('passenger_num') + form.instance.sharer_num > 6):
            return HttpResponse('no permission to edit, exceeding maximum vehicle capacity!')
        if(form.instance.status == 'confirmed'):
            return HttpResponse('no permission')        
        form.instance.owner = self.request.user
        form.instance.total_num = form.instance.sharer_num + form.instance.passenger_num
        form.instance.save()
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
        #form.instance.ride_order = 
        #form.save()
        return super().form_valid(form)

## for join operation
class ShareList(ListView):
    model = OrderInfo
    template_name = 'rides/shareorderlist.html'
    context_object_name = 'orders'
    ordering = ['arrival_date']
    def get_queryset(self):
        sharer = self.request.user.ridesharer_set.last()
        #target = RideSharer.objects.get(sharer=self.request.user)
        orders = OrderInfo.objects.filter(is_shared=True, dest_addr=sharer.dest_addr, arrival_date__lte=sharer.arrival_late, arrival_date__gte=sharer.arrival_early, status='open', ).exclude(owner=sharer.sharer)
        for order in orders:
            sharers = order.ridesharer_set.all()
            for ridesharer in sharers:
                if ridesharer.sharer == sharer.sharer:
                    orders = orders.exclude(id = order.id)
                    break
        return orders
        #order_result = OrderInfo.objects.filter(is_shared=True, dest_addr=sharer.dest_addr, arrival_date__lte=sharer.arrival_late, arrival_date__gte=sharer.arrival_early, status='open', ).exclude(owner=sharer.sharer)
        # if not order_result:
        #     return HttpResponse('Sorry! No order matched for you to join!')
        #return order_result

class ShareOrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/shareorderdetail.html'
    # template_name = 'rides/orderdetail.html'
    # context_object_name = 'order'

class SharerDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = RideSharer
    template_name = 'rides/sharer_confirm_delete.html'
    success_url = '/rides/rideuser/joinorders'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        sharer = self.get_object()
        sharer.ride_order.sharer_num = sharer.ride_order.sharer_num - sharer.passenger_num
        sharer.ride_order.total_num = sharer.ride_order.total_num - sharer.ride_order.sharer_num
        sharer.ride_order.save()
        return super(SharerDelete, self).delete(request, *args, **kwargs)
    def test_func(self):
        sharer = self.get_object()
        if self.request.user == sharer.sharer:
            return True
        return False


## for edit orders
class ShareOrderList(ListView):
    model = RideSharer
    template_name = 'rides/sharerlist.html'
    context_object_name = 'sharers'
    ordering = ['arrival_date']
    def get_queryset(self):
        return RideSharer.objects.filter(sharer=self.request.user)

class ShareHistoryDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/sharehistory.html'


# class ShareOrderList(ListView):
#     model = OrderInfo
#     template_name = 'rides/orderlist.html'
#     context_object_name = 'orders'
#     ordering = ['-arrival_date']
#     def get_queryset(self):
#         #sharer = self.request.user.ridesharer_set.last()
        
#         return OrderInfo.objects.filter(ridesharer_set__contains=self.request.user).exclude(status='complete').order_by('arrival_date')

#         #return OrderInfo.objects.filter(sharer_name=self.request.user.username).exclude(status='complete').order_by('arrival_date')


class DriverOrderList(ListView):
    model = OrderInfo
    template_name = 'rides/driverorderlist.html'
    context_object_name = 'orders'
    ordering = ['arrival_date']
    def get_queryset(self):
        driver = self.request.user.driverprofile
        return OrderInfo.objects.filter(plate_num=driver.plate_num, status='confirmed')


class DriverOrderDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/driverorderdetail.html'

def joinconfirm(request, order_id):
    sharer_toadd = request.user.ridesharer_set.last()
    order_toadd = OrderInfo.objects.filter(pk=order_id).first()
    # suppose the largest load of cars in our platform is 6
    if sharer_toadd.passenger_num + order_toadd.total_num > 6:
        messages.success(request,'Sorry! You cannot join this ride, it will be overloaded')
        return redirect('joinlist')
    order_toadd.sharer_num = order_toadd.sharer_num + sharer_toadd.passenger_num
    order_toadd.total_num = order_toadd.sharer_num + order_toadd.passenger_num
    #order_toadd.save()
    sharer_toadd.ride_order = order_toadd
    ##fill the share_name field of the orderinfo object
    order_toadd.sharer_name = sharer_toadd.sharer.username
    order_toadd.save()
    sharer_toadd.save()

    
    #form.instance.ride_order.sharer_name = self.request.user.username
    #sharer_toadd.save()
    messages.success(request,'You have joined a order successfully!')
    return redirect('joinorders')
    #return HttpResponse('confirm success')


class DriverList(ListView):
    model = OrderInfo
    template_name = 'rides/driver.html'
    context_object_name = 'orders'
    ordering = ['arrival_date']
    def get_queryset(self):
        driver = self.request.user.driverprofile
        #sharers = OrderInfo.ridesharer_set.filter(sharer=self.request.user)
        #curuser_sharers = self.request.user.ridesharer_set
        #.exclude(sharer__in=curuser_sharers)
        orders = OrderInfo.objects.filter(Q(vehicle_type=driver.vehicle_type)|Q(vehicle_type=''), Q(special_info=driver.special_info)|Q(special_info=''), status='open', total_num__lte=driver.vehicle_capacity).exclude(owner=driver.user)
        for order in orders:
            sharers = order.ridesharer_set.all()
            for sharer in sharers:
                if sharer.sharer == driver.user:
                    orders = orders.exclude(id = order.id)
                    break
        return orders

class DriverConfirmDetail(DetailView):
    model = OrderInfo
    template_name = 'rides/driverdetail.html'

def DriverConfirm(request, order_id):
    driver = request.user.driverprofile
    order = OrderInfo.objects.filter(pk=order_id).first()
    #order.shared_seats = driver.vehicle_capacity - order.passenger_num
    order.status = 'confirmed'
    order.driver_name = driver.name
    order.plate_num = driver.plate_num
    order.vehicle_type = driver.vehicle_type
    order.vehicle_capacity = driver.vehicle_capacity
    order.save()
    #send the email to sharer and owner
    subject = 'Your order had been confirmed by a driver!'
    message = 'Thank you for choosing us'
    email_from = settings.EMAIL_HOST_USER
    #send email to the sharer
    recipient_list1 = [order.owner.email]
    send_mail(subject,message,email_from,recipient_list1)
    #send email to the owner
    sharers = order.ridesharer_set.all()
    for sharer in sharers:
        recipient_list2 = [sharer.sharer.email]
        send_mail(subject,message,email_from,recipient_list2)

    messages.success(request,'confirm success, and notification email sent')
    return redirect('driverorderlist')
    #return HttpResponse('confirm success and notification email sent')

def DriverComplete(request, order_id):
    driver = request.user.driverprofile
    order = OrderInfo.objects.filter(pk=order_id).first()
    order.status = 'complete'
    order.save()
    messages.success(request,'Congratulations! You have already complete this order!')
    return redirect('driverorderlist')
    #return HttpResponse('complete success')

