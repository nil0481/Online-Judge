from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.models import User
from .models import Submissions
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class signupform(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2','email', 'first_name', 'last_name')



    def save(self, commit=True):
        user = super(signupform,self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CodeForm(ModelForm):
    class Meta:
        model = Submissions
        fields = ['user_code']
        widgets = {'user_code' : forms.Textarea()}