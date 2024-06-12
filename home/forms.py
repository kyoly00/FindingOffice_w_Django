# forms.py
from django import forms
from .models import Customer
from .models import Reservation

class SignUpForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'cus_password', 'cus_name', 'cus_gender',
            'cus_email', 'cus_company', 'cus_phone', 'cus_address',
        ]
        widgets = {
            'cus_password': forms.PasswordInput(),
            'cus_email': forms.EmailInput(),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['re_start_time', 're_end_time']
        widgets = {
            're_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            're_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }