from django.urls import path

from .views import check_self

urlpatterns = [
    path("self/", check_self, name="check_self"),
]