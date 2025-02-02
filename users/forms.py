import uuid

from allauth.account.forms import SignupForm, ResetPasswordForm, ChangePasswordForm, AddEmailForm
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib.auth import get_user, password_validation, get_user_model
from django.core.exceptions import ValidationError
from allauth.account.utils import get_adapter, send_email_confirmation
from .models import Profile
import os
from PIL import Image

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


class CustomEmailChangeForm(forms.Form):
    email1 = forms.EmailField(label='New Email')
    email2 = forms.EmailField(label='Confirm New Email')

    def clean(self):
        User = get_user_model()
        cleaned_data = super().clean()
        email1 = cleaned_data.get("email1")
        email2 = cleaned_data.get("email2")

        if email1 and email2:
            # Clean emails using adapter
            email1 = get_adapter().clean_email(email1)
            email2 = get_adapter().clean_email(email2)

            # Check if emails match
            if email1 != email2:
                raise forms.ValidationError("Emails do not match")

            # Comprehensive email uniqueness check
            if (User.objects.filter(email=email1).exists() or
                    EmailAddress.objects.filter(email=email1).exists() or
                    SocialAccount.objects.filter(user__email=email1).exists()):
                raise forms.ValidationError("Email already in use")

            cleaned_data['email1'] = email1
            cleaned_data['email2'] = email2

        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('nickname', 'bio', 'avatar')

    avatar = forms.ImageField(required=False)

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if not nickname:
            raise forms.ValidationError("Nickname is required")

        # If this is an existing profile being updated, exclude it from the unique check
        existing_profile = Profile.objects.filter(nickname=nickname)
        if self.instance.pk:
            existing_profile = existing_profile.exclude(pk=self.instance.pk)

        if existing_profile.exists():
            raise forms.ValidationError("This nickname is already registered")

        return nickname

    def clean_avatar(self):
        img = self.cleaned_data.get('avatar')
        if not img:
            return img  # Return if no new image

        # Check file extension
        extension = os.path.splitext(img.name)[1].lower()
        if extension not in settings.ALLOWED_IMAGE_FILETYPES:
            raise forms.ValidationError("Invalid image extension")

        return img

    def save(self,commit=True):
        profile=super().save(commit=False)

        if self.cleaned_data.get('avatar'):
            img=self.cleaned_data.get('avatar')
            extension = os.path.splitext(img.name)[1].lower()
            filename=f'{uuid.uuid4()}.{extension.lower()}'

            image=Image.open(img)
            img.thumbnail((200,200))

            save_path=os.path.join(settings.MEDIA_ROOT, 'avatars',filename)
            image.save(save_path)
            profile.avatar=os.path.join('avatars',filename)

        if commit:
            profile.save()

        return profile