from django.urls import path, include, re_path
from . import views
import re

urlpatterns = [
    path("", views.initial_menu, name = "initial_menu"),
    path("register", views.register, name = "register"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("postlogin/", views.postlogin, name = "postlogin"),
    path('logout_extension/', views.logout_extension, name='logging_out'),
    path("home/", views.home, name = "home"),
    path('verificar-correo', views.verification, name = "verification"),
    #path('verification-counter', views.verification_counter, name='verification-counter'),
    
]

