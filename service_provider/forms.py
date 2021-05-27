from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from service_provider import models


# User auth
class UserAuthenticationForm(forms.Form):
    id = forms.CharField(max_length=150, required=True)
    password = forms.CharField(max_length=128, required=True)

    def authenticate(self):
        return auth.authenticate(username=self.cleaned_data['id'], password=self.cleaned_data['password'])


# User
class MinimalUserForm(UserAuthenticationForm):
    display_name = forms.CharField(max_length=200, required=True)
    email = forms.EmailField(max_length=254, required=True)


class FullUserForm(UserAuthenticationForm):
    display_name = forms.CharField(max_length=200, required=False)
    email = forms.EmailField(max_length=254, required=False)
    gender = forms.BooleanField(required=False)
    status = forms.CharField(required=False)


class PasswordChangeForm(UserAuthenticationForm):
    new_password = forms.CharField(max_length=128, required=True)


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['display_name', 'gender', 'status']


# Photo blog
class PhotoBlogForm(UserAuthenticationForm):
    title = forms.CharField(max_length=300, required=False)
    description = forms.CharField(required=False)
    image = forms.ImageField(required=True)
    ext = forms.CharField(required=True)
    score = forms.FloatField(required=False)
    positions = forms.CharField(required=True)


class PhotoValidationForm(UserAuthenticationForm):
    photo_id = forms.IntegerField(required=True)


class PhotoUpdateForm(PhotoValidationForm):
    title = forms.CharField(max_length=300, required=False)
    description = forms.CharField(required=False)
    score = forms.FloatField(required=False)


class PhotoDeleteForm(PhotoValidationForm):
    fake_delete = forms.BooleanField(required=False)
