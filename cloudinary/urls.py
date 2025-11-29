from django.urls import path
from .views import upload, display

urlpatterns = [
    path("upload_image/", upload, name = "uploadImage"),
    path("display_images/", display, name = "displayImages"),
]
