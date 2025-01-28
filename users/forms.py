from allauth.account.forms import SignupForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib.auth import get_user, password_validation
from django.core.exceptions import ValidationError
from allauth.account.utils import get_adapter, send_email_confirmation
import os
class ResendEmailForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 text-gray-700',
            'placeholder': 'Enter your email address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        email = get_adapter().clean_email(email)

        # Check if email exists in the system
        if not EmailAddress.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email address")

        # Check if email is already verified
        if EmailAddress.objects.filter(email=email, verified=True).exists():
            raise forms.ValidationError("This email is already verified")

        # Check if associated with social account
        if SocialAccount.objects.filter(user__email=email).exists():
            raise forms.ValidationError("This email is associated with a social account. Please login using your social account.")

        return email