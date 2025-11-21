from django.urls import path
from . import views

urlpatterns = [
    path('<slug:slug>/', views.index, name='index'),
]