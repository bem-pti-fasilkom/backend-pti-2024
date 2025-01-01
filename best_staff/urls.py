from django.urls import path
from . import views

urlpatterns = [
    path('authenticate/', views.authenticate_staff, name='authenticate'),
    path('event/', views.get_event, name='event'),
]