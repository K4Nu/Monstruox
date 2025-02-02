from django.urls import path, include
from . import views
from Monstruox import settings
from . import views
app_name = 'users'

urlpatterns = [
    path("create_profile/", views.CreateProfile.as_view(), name="create_profile"),
    #path("profile/<pk:int>/",views.ProfileDashboard.as_view(), name="profile"),
    path("delete_profile/<int:pk>/", views.DeleteUser.as_view(), name="delete_profile"),
    ]

