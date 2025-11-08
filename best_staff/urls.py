from django.urls import path
from . import views
from .views import VoteAPIView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('authenticate/', views.authenticate_staff, name='authenticate'),
    path('event/', views.get_event, name='event'),
    path('birdept/', views.get_birdept, name='birdept'),
    path('birdept/member/', views.get_birdept_member, name='birdept_member'),
    path('vote/<str:voted_npm>/', VoteAPIView.as_view(), name='vote'),
    path('vote/statistics/<str:birdept>/', VoteAPIView.as_view(), name='vote_statistics'),
    path('statistics/', views.get_all_statistics, name='all_vote_statistics'),

    # Endpoint buat API documentation
    path('docs/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]