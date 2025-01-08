from django.urls import path
from . import views
from .views import VoteAPIView

urlpatterns = [
    path('authenticate/', views.authenticate_staff, name='authenticate'),
    path('event/', views.get_event, name='event'),
    path('birdept/', views.get_birdept, name='birdept'),
    path('npm_whitelist/', views.get_npm_whitelist, name='npm_whitelist'),
    path('birdept/member/', views.get_birdept_member, name='birdept_member'),
    path('vote/<str:voted_npm>/', VoteAPIView.as_view(), name='vote'),
    path('vote/statistics/<str:birdept>/', VoteAPIView.as_view(), name='vote_statistics'),
]