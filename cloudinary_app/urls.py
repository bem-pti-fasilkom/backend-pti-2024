from django.urls import path
from .views import *

urlpatterns = [
    path("image/", CloudinaryImageGetCreate.as_view(), name = "uploadNgetAllImages"),
    path("image/<uuid:id>/", CloudinaryImageGetCreate.as_view(), name = "getImageById"),
    path("video/", CloudinaryVideoGetCreate.as_view(), name = "uploadNgetAllVideos"),
    path("video/<uuid:id>/", CloudinaryVideoGetCreate.as_view(), name = "getVideoById"),
]
