"""
URL configuration for issue_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .settings import ENVIRONMENT

from issue_tracker import views

# Create routes for different viewsets
router = routers.SimpleRouter()
router.register("pengaduan", views.PengaduanViewSet, basename="pengaduan")

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("staging/", include(router.urls)) if ENVIRONMENT == "development" else path("api/", include(router.urls)),
    path("auth/", include("jwt.urls")),
]
