from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
    
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(
        max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(
        max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2',)
        
class CodeForm(forms.Form):
    code = forms.IntegerField(max_value= '999999', required= False, help_text= 'Introduce the 6 digits code of Google Authenticator.')
    class Meta:
        fields = ('code',)

class VerificationForm(forms.Form):
    secuence = forms.CharField(max_length= 32, required= True, help_text= 'Introduce the code that you have received in your email.', label="Secuence")
    class Meta:
        fields = ('secuence',)