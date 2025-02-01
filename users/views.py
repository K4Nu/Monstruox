from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, View, TemplateView, FormView, DeleteView, CreateView
from django import forms
import os
from django.contrib import messages
from .forms import ResendEmailForm, CustomEmailChangeForm, ProfileForm
from allauth.account.views import PasswordChangeView, EmailView, PasswordResetFromKeyDoneView, ConfirmEmailView, \
    SignupView,PasswordResetView,LoginView,PasswordResetDoneView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages import get_messages
from django.contrib.auth import logout,login,authenticate
from allauth.account.utils import get_adapter
from django.db import transaction
from django.forms import modelform_factory
from django.core.validators import validate_email
from django.db.models import Q
from .models import Profile

class ResendVerificationEmail(FormView):
    template_name = "users/resend_email_verification.html"
    form_class = ResendEmailForm  # Use form_class instead of form

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        email = get_adapter().clean_email(email)
        query = EmailAddress.objects.filter(email=email).first()

        if query and not query.verified:
            send_email_confirmation(self.request, query.user,
                                    email=email)  # Use query.user instead of self.users.first()
            return redirect("users:update_profile")

        messages.error(self.request, "Email not found or already verified.")
        return redirect("users:resend_email_verification")

class IndexView(TemplateView):
    template_name = "users/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ProfileForm()
        try:
            Profile.objects.get(user=self.request.user)
            context["has_profile"]=True
        except Profile.DoesNotExist:
            context["has_profile"]=False
        return context


class ConfirmEmailView(ConfirmEmailView,):
    def get(self, request, *args, **kwargs):
        try:
            # Get and confirm the email confirmation object
            self.object = self.get_object()
            self.object.confirm(self.request)

            # Clear any existing messages
            storage = get_messages(self.request)
            for message in storage:
                pass  # Clear existing messages

            # Add success message
            messages.success(request, "Email has been confirmed successfully.")

            return redirect("account_login")

        except Exception as e:
            messages.error(request, "Invalid or expired confirmation link.")
            return redirect("account_login")

class CustomEmailView(FormView):
    template_name = "account/email.html"
    form_class = CustomEmailChangeForm
    success_url = reverse_lazy("users:profile_view")

    def dispatch(self, request, *args, **kwargs):
        if SocialAccount.objects.filter(user=self.request.user).exists():
            messages.error(request, "You cannot change your email using a social account.")
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email1']  # Already cleaned by form
        user = self.request.user

        # Email uniqueness is already checked in form's clean method
        if user.email != email:
            with transaction.atomic():
                # Update existing email addresses
                EmailAddress.objects.filter(user=user).delete()
                EmailAddress.objects.create(user=user, email=email, primary=True, verified=False)

                # Update user email
                user.email = email
                user.save()

                # Send confirmation email
                send_email_confirmation(self.request, user, email=email)
                messages.success(self.request, "Email has been changed successfully. Check your email to confirm your email.")
                logout(self.request)

        return super().form_valid(form)

class PasswordResetDoneView(PasswordResetDoneView):
    def get(self,request,*args,**kwargs):
        storage = get_messages(self.request)
        for message in storage:
            pass
        messages.success(self.request, "Password reset link sent successfully.")
        return redirect("login")

class PasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    def get(self,request,*args,**kwargs):
        storage = get_messages(self.request)
        for message in storage:
            pass
        messages.success(self.request, "Password has been changed successfully.")
        return redirect("login")

class CreateProfile(CreateView):
    template_name = "users/create_profile.html"
    model = Profile
    form_class = ProfileForm

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()

        if self.request.headers.get('HX-Request'):
            # Return a response that will trigger a page refresh
            return HttpResponse(
                '<script>window.location.href = "/";</script>',
                headers={
                    'HX-Trigger': 'profileCreated'
                }
            )
        return redirect("index")

    def form_invalid(self, form):
        if self.request.headers.get('HX-Request'):
            # Return just the form with errors for HTMX to update
            context = {'form': form}
            return render(
                self.request,
                'users/partials/profile_form.html',  # Create this template
                context,
                status=400
            )
        return super().form_invalid(form)

class ProfileDashboard(DetailView):
    model = Profile
    template_name = "users/dashboard.html"
    context_object_name = "profile"


class ProfileDelete(DeleteView):
    model = Profile
    success_url = reverse_lazy("index")

    # Do not specify template_name if you're not using a confirmation page.

    def get(self, request, *args, **kwargs):
        # WARNING: This deletes the object on GET request.
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Profile has been deleted successfully.")
        return super().delete(request, *args, **kwargs)