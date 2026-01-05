from django.urls import path
from .views import *

urlpatterns = [
    path("image/", CloudinaryImageGetCreate.as_view(), name = "uploadAndGetImage"),
    path("image/<uuid:id>/", CloudinaryImageGetCreate.as_view(), name = "getImageById"),
    path("video/", CloudinaryVideoGetCreate.as_view(), name = "uploadAndGetVideo"),
    path("video/<uuid:id>/", CloudinaryVideoGetCreate.as_view(), name = "getVideoById"),
]
