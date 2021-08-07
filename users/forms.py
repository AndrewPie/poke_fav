from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1','password2']
    def save(self,commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.clean_password2())
        user.is_active=False
        if commit:
            user.save()
            return user


class LoginForm(forms.Form):
    username=forms.CharField(max_length=64)
    password=forms.CharField(max_length=64,widget=forms.PasswordInput())