from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import WomanUser

class WomanRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = WomanUser
        fields = ['username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'age', 'gender', 
                 'phone_number', 'emergency_contact', 'address']

class WomanLoginForm(AuthenticationForm):
    class Meta:
        model = WomanUser
        fields = ['username', 'password']
        
from django import forms
from .models import WomanUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = WomanUser
        fields = [
            'first_name', 'last_name', 'email',
            'age', 'gender', 'phone_number', 'emergency_contact',
            'address', 'profile_picture',
        ]

