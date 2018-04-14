from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.safestring import mark_safe
from django_password_strength.widgets import (
    PasswordStrengthInput,
    PasswordConfirmationInput
)
import re

from . import models


class UserExtendedCreationForm(UserCreationForm):
    verify_email = forms.EmailField(label="Please verify your email address")

    class Meta:
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'verify_email',
            'password1',
            'password2'
        ]
        model = User

    def clean(self):
        data = self.cleaned_data
        email = data.get('email')
        verify = data.get('verify_email')

        if email != verify:
            raise forms.ValidationError("You must enter the same email in both fields.")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = [
            'first_name',
            'last_name',
            'email',
            'confirm_email',
            'birth_date',
            'country',
            'city',
            'fav_animal',
            'hobby',
            'bio',
            'avatar'
        ]

    confirm_email = forms.EmailField(
        label="Confirm email"
    )

    birth_date = forms.DateField(
        label="Date of Birth",
        input_formats=['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'],
        widget=forms.TextInput(
            attrs={'placeholder': 'Valid formats (YYYY-MM-DD, MM/DD/YYYY, or MM/DD/YY)'}
        )
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write a short bio about you'}),
        min_length=10,
        label="Biography"
    )

    country = forms.CharField(
        label="Country"
    )

    city = forms.CharField(
        label="City of residence"
    )

    fav_animal = forms.CharField(
        max_length=40,
        label='Favorite Animal'
    )

    hobby = forms.CharField(
        max_length=40,
        label='Hobby'
    )

    def clean(self):
        data = self.cleaned_data
        email = data.get('email')
        verify = data.get('confirm_email')

        if email != verify:
            raise forms.ValidationError("You must enter the same email in both fields.")


class StrongPasswordChangeForm(PasswordChangeForm):
    """Form for changing user's password."""
    MIN_LENGTH = 14

    new_password1 = forms.CharField(
        widget=PasswordStrengthInput(attrs={'placeholder': 'New password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=PasswordConfirmationInput(
            attrs={'placeholder': 'Confirm new password'},
            confirm_with='new_password1'
        ),
        label='Confirm Password'
    )

    class Meta:
        fields = ['new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(StrongPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = mark_safe(
            '<ul>\n'
            '<li>Must not be the same as the current password</li>\n'
            '<li>Minimum password length of 14 characters</li>\n'
            '<li>Must use both uppercase and lowercase letters</li>\n'
            '<li>Must include one or more numerical digits</li>\n'
            '<li>Must include at least one special character, such as @, #, or'
            ' $</li>\n'
            "<li>Cannot contain your username or parts of your full name, "
            'such as your first name</li>\n'
            '</ul>'
        )

    def clean(self):
        user = self.request.user
        new_password = self.cleaned_data.get('new_password1')
        old_password = self.cleaned_data.get('old_password')

        # Must not be the same as the current password
        if user.check_password(old_password):
            if new_password == old_password:
                raise forms.ValidationError(
                    "New password cannot match the old password.")
        else:
            raise forms.ValidationError("Your old password was entered "
                                        "incorrectly. Please enter it again. ")

        # Must use both uppercase and lowercase letters
        if not re.search('([a-z])+', new_password) or \
                not re.search('([A-Z])+', new_password):
            raise forms.ValidationError("The new password must use both "
                                        "uppercase and lowercase letters.")

        # Minimum password length of 14 characters
        if len(new_password) < self.MIN_LENGTH:
            raise forms.ValidationError(
                "The new password must be at least %d characters long." %
                self.MIN_LENGTH
            )

        # Must include of one or more numerical digits
        if not re.search('\d+', new_password):
            raise forms.ValidationError("The new password must include one or "
                                        "more numerical digits.")

        # Must include of special characters, such as @, #, $
        if not re.search('([@#$])+', new_password):
            raise forms.ValidationError("The new password must include the at "
                                        "least one of the following characters: @, #, or $.")

        # Cannot contain parts of the username or first and last name
        user_first_name = models.UserProfile.objects.get(user=self.request.user).first_name.lower()
        user_last_name = models.UserProfile.objects.get(user=self.request.user).last_name.lower()
        user_username = str(self.request.user).lower()

        if (user_first_name in new_password.lower() or user_last_name in
                new_password.lower() or user_username in new_password.lower()):
            raise forms.ValidationError("The new password cannot contain your "
                                        "username ({}) or parts of your full name ({} {}).".format(
                user.username, user.first_name, user.last_name))

        return self.cleaned_data

