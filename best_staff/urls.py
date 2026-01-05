from django.urls import path
from . import views

urlpatterns = [
    path('authenticate/', views.authenticate_staff, name='authenticate'),
    path('event/', views.get_event, name='event'),
    path('birdept/', views.get_birdept, name='birdept'),
    path('birdept/members/', views.get_birdept_member, name='birdept_member'),
    path('vote/<str:voted_npm>/', views.create_vote, name='vote'),
    path('statistics/<str:birdept>/', views.get_statistic, name='vote_statistics'),
    path('statistics/', views.get_all_statistics, name='all_vote_statistics'),
    path('winners/', views.get_all_winners, name='all_winners'),
]