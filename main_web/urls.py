from django.urls import path
from . import views

urlpatterns = [
   path('', views.ReadEvent.as_view(), name='events'),
    path('<int:id>/', views.ReadEventDetail.as_view(), name='event_detail'),
]