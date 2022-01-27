from contextvars import Context
from django.shortcuts import redirect, render
from .models import OrderInfo, RideOwner
from users.models import DriverProfile
from .forms import OrderInfoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def home(request):
    return render(request, 'rides/home.html')

def userhome(request):
    return render(request, 'rides/userhome.html')

def sharer(request):
    return render(request, 'rides/sharer.html')

def driver(request):
    ride_driver = DriverProfile.objects.filter(user=request.user.id)
    if ride_driver.plate_num == '':
        return render(request, 'rides/driver_register.html')
    else:
        return render(request, 'rides/driver.html')

@login_required       
def request_ride(request):
    if request.method == 'POST':
        form=OrderInfoForm(request.POST,request.user.username)
        if form.is_valid():
            instance = form.instance
            instance.username = request.user.username
            instance.userid = request.user.id
            #instance.user = request.user
            instance.save()
            #setusername=form.cleaned_data['username']
            form.save()
            instance.rideowner.user = request.user
            instance.save()
            username=request.user.username
            # new_orderinfo = request.orderinfo
            # new_orderinfo.username=request.user.username
            # new_orderinfo.save()
            messages.success(request,f'Welcome {username}! Your account has been created! Congratulations to join bbRide!')
            return redirect('login')
    else:
        form = OrderInfoForm()
    return render(request, 'rides/order_form.html', {'form': form})

@login_required       
def request_edit(request):
    if request.method == 'POST':
        form=OrderInfoForm(request.POST,request.user.username)
        if form.is_valid():
            instance = form.instance
            instance.username = request.user.username
            instance.userid = request.user.id
            #instance.user = request.user
            instance.save()
            #setusername=form.cleaned_data['username']
            form.save()
            instance.rideowner.user = request.user
            instance.save()
            username=request.user.username
            # new_orderinfo = request.orderinfo
            # new_orderinfo.username=request.user.username
            # new_orderinfo.save()
            messages.success(request,f'Welcome {username}! Your account has been created! Congratulations to join bbRide!')
            return redirect('login')
    else:
        form = OrderInfoForm()
    return render(request, 'rides/order_form.html', {'form': form})

# def orderlist(request):
#     orders = OrderInfo.objects.filter(OrderInfo.status!='complete')
#     context = {
#         'orders' : orders,
#     }
#     return render(request,'rides/oderlist.html',context)

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
        form.save()
        return super().form_valid(form)

class OrderUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OrderInfo
    template_name = 'rides/order_form.html'
    fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super().form_valid(form)