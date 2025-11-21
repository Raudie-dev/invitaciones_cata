from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear/', views.crear_invitacion_mesa, name='crear_invitacion_mesa'),
    path('agregar-invitado/', views.agregar_invitado, name='agregar_invitado'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('export-confirmed-guests/', views.export_confirmed_guests, name='export_confirmed_guests'),
]