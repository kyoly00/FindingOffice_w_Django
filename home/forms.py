# forms.py
from django import forms
from .models import Customer

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
