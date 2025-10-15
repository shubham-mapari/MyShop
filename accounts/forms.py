# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AdminRegistrationForm(UserCreationForm):
    # Additional fields for admin profile
    mobile = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Mobile Number'})
    )
    shop_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Shop Name'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Address', 'rows': 3})
    )
    admin_role = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Role (e.g., Manager, Owner)'})
    )
    security_question = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Security Question'})
    )
    
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    def clean_mobile(self):
        """Validate mobile number"""
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")
        if mobile and len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be 10 digits.")
        return mobile
