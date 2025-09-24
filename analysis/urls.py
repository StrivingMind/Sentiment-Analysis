from django.contrib import admin
from django.urls import path
from analysis import views
urlpatterns = [
    path('', views.index, name='analysis'),
]