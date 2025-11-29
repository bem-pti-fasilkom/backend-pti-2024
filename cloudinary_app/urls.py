from django.urls import path
from .views import *

urlpatterns = [
    path("image/", CloudinaryImageGetCreate.as_view(), name = "uploadImage"),
    path("image/<uuid:id>/", CloudinaryImageGetCreate.as_view(), name = "uploadImage"),
    path("video/", CloudinaryVideoGetCreate.as_view(), name = "displayImages"),
    path("video/<uuid:id>/", CloudinaryVideoGetCreate.as_view(), name = "displayImages"),
]
