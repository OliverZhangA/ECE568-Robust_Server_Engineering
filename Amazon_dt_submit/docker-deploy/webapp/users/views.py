# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegistrationForm, UsersForm, DriversForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DriverProfile



def register(request):
    if request.method == 'POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f'Welcome {username}! Your account has been created! Congratulations to join BBshopping!')
            return redirect('login')

    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def driverform(request):
    # if not request.user.is_authenticated():
    #     messages.success(request,'Please log in first!')
    #     return redirect('login')
    if request.method == 'POST':
        #get the form saved in the current log in user
        curuser = User.objects.get(pk=request.user.id)
        curdriverprofile = DriverProfile.objects.get(user=request.user.id)
        form_user=UsersForm(request.POST,instance=curuser)
        #get the form saved in the current log in driver(correspond to current user)
        form_driver=DriversForm(request.POST,request.FILES, instance=curdriverprofile)
        if form_user.is_valid() and form_driver.is_valid():
            form_driver.save()
            form_user.save()
            username=request.user.username
            # username=form_user.cleaned_data.get('username')
            # userid=form_user.cleaned_data.get('userid')
            messages.success(request,f' {username}, you have already updated your customer information!')
            return redirect('driverprofile')
    else:
        curuser = User.objects.get(pk=request.user.id)
        curdriverprofile = DriverProfile.objects.get(user=request.user.id)
        form_user=UsersForm(instance=curuser)
        form_driver=DriversForm(instance=curdriverprofile)
    context = {
        'form_user': form_user,
        'form_driver': form_driver
    }
    return render(request,'users/driverprofile.html',context)

@login_required
def buy(request):
    return render(request, "users/buy.html")