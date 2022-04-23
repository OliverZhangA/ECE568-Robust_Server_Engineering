from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DriverProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

#create model forms
class UsersForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class DriversForm(forms.ModelForm):
    class Meta:
        model = DriverProfile
        fields = ['dest_x','dest_y','UPS_account','cardnum','seccode','valid_date']