from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from users.validators import validate_phone
from users.models import User

class CustomUserCreationForm(UserCreationForm):
    country = forms.CharField(max_length=2,required=False)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('role_management','phone_number','email')
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        country = self.cleaned_data.get('country')
        valid_number = validate_phone(phone_number, country)
        return valid_number
    
    def clean_password2(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return super().clean_password2()
    
class CustomUserChangeForm(UserChangeForm):
    country = forms.CharField(max_length=2,required=False)
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('role_management','phone_number','email')
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        country = self.cleaned_data.get('country')
        valid_number = validate_phone(phone_number, country)
        return valid_number