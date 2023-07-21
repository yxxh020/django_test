from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),  # function based view(FBV)
]