from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, View, TemplateView, FormView, DeleteView
from django import forms
import os
from django.contrib import messages
from .forms import ResendEmailForm
from allauth.account.views import PasswordChangeView, EmailView, PasswordResetFromKeyDoneView, ConfirmEmailView, \
    SignupView,PasswordResetView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages import get_messages
from django.contrib.auth import logout
from allauth.account.utils import get_adapter
from django.db import transaction
from django.forms import modelform_factory

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
