# users/forms.py

# this is the form that will be used to update the user's profile
# it includes:
# 1. custom form fields for log in and sign up
# 2. a form for updating the user's profile
# 3. a form for changing the user's password

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError
import re

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

class CustomSignupForm(UserCreationForm):
    """
    Custom form for signing up a new user.

    1. The username field is required and must be between 3 to 20 characters long. It can only contain letters and numbers.
    2. The password field is required and must be between 8 to 30 characters long. It must contain at least one number and one special character.
    3. The confirm password field is required and must match the password field.
    """

    username = forms.CharField(max_length=20, min_length=3, required=True, help_text='Required. 3 to 20 characters. Letters and numbers only.')
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput, help_text='Required. 8 to 30 characters. Must include 1 number and 1 special character.')
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, help_text='Enter the same password as before, for verification.')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        """
        1. get the username from the cleaned data
        2. check if the username only contains letters and numbers
        3. check if the username already exists
        """
        username = self.cleaned_data['username'].strip()
        if not re.match(r'^\w+$', username):
            raise ValidationError("Username can only contain letters and numbers.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean_password2(self):
        """
        1. get the password1 and password2 from the cleaned data
        2. check if the passwords match
        3. check if the password contains at least one number
        4. check if the password contains at least one special character
        5. check if the password is between 8 to 30 characters long
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")

        if not re.search(r'\d', password1):
            raise ValidationError("The password must contain at least one number.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("The password must contain at least one special character.")
        
        if len(password1) < 8 or len(password1) > 30:
            raise ValidationError("Password must be between 8 to 30 characters long.")
        
        return password2


class ProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Profile'))


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Change Password'))