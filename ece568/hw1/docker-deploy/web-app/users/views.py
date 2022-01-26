# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegistrationForm, UsersForm, DriversForm


def register(request):
    if request.method == 'POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f'Welcome {username}! Your account has been created! Congratulations to join bbRide!')
            return redirect('login')

    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def driverform(request):
    if request.method == 'POST':
        #get the form saved in the current log in user
        form_user=UsersForm(request.POST,request.user)
        #get the form saved in the current log in driver(correspond to current user)
        form_driver=DriversForm(request.POST,request.user.driver)
        if form_user.is_valid() and form_driver.is_valid():
            form_driver.save()
            form_user.save()
            username=form_user.cleaned_data.get('username')
            messages.success(request,f'Driver {username}, you have already updated your driver information!')
            return redirect('driver')
    else:
        form_user=UsersForm()
        form_driver=DriversForm()
    context = {
        'form_user': form_user,
        'form_driver': form_driver
    }
    return render(request,context=context,template_name='users/driver_updateform.html')
