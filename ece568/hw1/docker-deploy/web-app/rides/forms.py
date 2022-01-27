from .models import OrderInfo
from django import forms

class OrderInfoForm(forms.ModelForm):
    class Meta:
        model = OrderInfo
        fields = ['dest_addr', 'arrival_date', 'passenger_num', 'vehicle_type', 'is_shared', 'special_info']