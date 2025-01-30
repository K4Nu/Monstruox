from allauth.account.forms import SignupForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib.auth import get_user, password_validation, get_user_model
from django.core.exceptions import ValidationError
from allauth.account.utils import get_adapter, send_email_confirmation
from .models import Profile


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

class CustomSignUpForm(SignupForm):
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            raise ValidationError({
                'email': 'This email is already registered.'
            })

        if User.objects.filter(username=username).exists():
            raise ValidationError({
                'username': 'This username is already registered.'
            })

        return cleaned_data

    def save(self, request):
        # Let the parent class handle the actual user creation
        user = super().save(request)
        return user

