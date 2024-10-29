from django.urls import path
from . import views

urlpatterns = [
    path('pengaduan/', views.CRPengaduanAPIView.as_view(), name='pengaduan'),
    path('pengaduan/histories/', views.get_my_pengaduan, name='my-pengaduan'),
    path('pengaduan/liked/', views.get_my_liked_pengaduan, name='liked-pengaduan'),
    path('pengaduan/commented/', views.get_my_commented_pengaduan, name='commented-pengaduan'),
    path('pengaduan/<int:id>/like/', views.LikePengaduanAPIView.as_view(), name='like-pengaduan'),
    path('pengaduan/<int:id>/', views.RUDPengaduanAPIView.as_view(), name='pengaduan_detail')
]