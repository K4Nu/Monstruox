"""
URL configuration for Monstruox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from allauth.account.views import LoginView, SignupView,LogoutView
from django.conf import settings
from django.conf.urls.static import static
from users.views import ConfirmEmailView
urlpatterns = [
    path("",user_views.IndexView.as_view(), name="index"),
    path("user/",include("users.urls"),name="user"),
    path('admin/', admin.site.urls),
    path("login/",LoginView.as_view(),name="login"),
    path("register/",SignupView.as_view(),name="register"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("accounts/password/reset/done/",user_views.PasswordResetDoneView.as_view(),name="password_reset_done"),
    path("accounts/password/reset/key/done/",user_views.PasswordResetFromKeyDoneView.as_view(),name="password_reset_from_key_done"),
    path('accounts/email/', user_views.CustomEmailView.as_view(), name='account_email'),
    path("accounts/confirm-email/<str:key>/", user_views.ConfirmEmailView.as_view(), name="account_confirm_email"),
    path("accounts/confirm-email/", ConfirmEmailView.as_view(), name="confirm_email"),
    path("accounts/resend-email-verification", user_views.ResendVerificationEmail.as_view(),
         name="resend_email_verification"),

    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

