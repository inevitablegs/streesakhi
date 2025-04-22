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

from django import forms
from .models import NutritionEntry

class NutritionEntryForm(forms.ModelForm):
    class Meta:
        model = NutritionEntry
        fields = ['date', 'time_slot', 'description']
        widgets = {
            'date':      forms.DateInput(attrs={'type': 'date'}),
            'time_slot': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 2}),
        }

# maa/forms.py

from django import forms

# example choices—you can expand this list as you like
FOOD_CHOICES = [
    ('',              '–– Select food/drink ––'),
    ('Water',         'Water'),
    ('Milk',          'Milk'),
    ('Tea',           'Tea'),
    ('Juice',         'Juice'),
    ('Fruit',         'Fruit'),
    ('Salad',         'Salad'),
    ('Sandwich',      'Sandwich'),
    ('Yogurt',        'Yogurt'),
    ('Other',         'Other…'),
]

class NutritionDayForm(forms.Form):
    date             = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    morning_choice   = forms.ChoiceField(choices=FOOD_CHOICES, required=False)
    morning_manual   = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'If not above…'}))
    noon_choice      = forms.ChoiceField(choices=FOOD_CHOICES, required=False)
    noon_manual      = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'…or type here'}))
    evening_choice   = forms.ChoiceField(choices=FOOD_CHOICES, required=False)
    evening_manual   = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'…'}))
    night_choice     = forms.ChoiceField(choices=FOOD_CHOICES, required=False)
    night_manual     = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'…'}))
