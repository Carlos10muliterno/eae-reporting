from django.urls import path
from . import views

urlpatterns = [
    path('', views.contactFormView, name="contact"),
]