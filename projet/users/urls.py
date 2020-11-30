"""projet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from users import views
from users.views import LoginApiView
from rest_framework import routers

router = routers.SimpleRouter()

urlpatterns = [
    path("login/", LoginApiView.as_view(), name="login"),
    path("create/", views.UserCreate.as_view(), name="create"),
    path("list-users/", views.ListUsers.as_view(), name="list-users"),
    path("profile/", views.ProfileList.as_view(), name="profile"),
    path("send-invite/", views.invite, name="invite"),
]
