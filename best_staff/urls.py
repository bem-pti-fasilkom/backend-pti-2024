from django.urls import path
from . import views

urlpatterns = [
    path('authenticate/', views.authenticate_staff, name='authenticate'),
    path('event/', views.get_event, name='event'),
    path('birdept/', views.get_birdept, name='birdept'),
    path('birdept/member/', views.get_birdept_member, name='birdept_member'),
    path('vote/<str:voted_npm>/', views.vote, name='vote'),
    path('vote/statistics/<str:birdept>', views.get_vote, name='vote_statistics'),
]