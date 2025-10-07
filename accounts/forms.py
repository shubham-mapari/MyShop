# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AdminUser

class AdminRegistrationForm(UserCreationForm):
    # Optional: add custom widgets or labels if needed
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    )

    class Meta:
        model = AdminUser
        fields = [
            'username',
            'first_name',
            'mobile',
            'email',
            'shop_name',
            'address',
            'role',
            'security_question',
            'password1',
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Mobile Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'shop_name': forms.TextInput(attrs={'placeholder': 'Shop Name'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address'}),
            'role': forms.Select(),
            'security_question': forms.TextInput(attrs={'placeholder': 'Security Question'}),
        }

    # Optional: add custom validation
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be 10 digits.")
        return mobile
