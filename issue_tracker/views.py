from django.shortcuts import get_object_or_404
from .serializers import CommentSerializer, PengaduanSerializer, UserSerializer
from .models import Pengaduan
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework import viewsets, status as HttpStatus
from jwt.lib import with_auth

class PengaduanViewSet(viewsets.ModelViewSet):
    serializer_class = PengaduanSerializer
    queryset = Pengaduan.objects.all()

    @with_auth
    def retrieve(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)

        # If the user desires to stay anonymous, do not return user object
        if pengaduan.anonymous :
            pengaduan.user = None
            pengaduan.save()

        ## Used to format datetime into a more readable format
        # unformatted_date = pengaduan.__getattribute__("tanggal_post")
        # pengaduan.__setattr__("tanggal_post", unformatted_date.strftime("%Y-%m-%d, %X"))

        return Response(serializer.data)
    
    def update(self, request, pk=None) :
        # User biasa : Judul, isi, lokasi (status = unresolved)
        # Admin : Status
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)

        if pengaduan.Status.UNRESOLVED :
            judul = request.data['judul']
            isi = request.data['isi']
            lokasi = request.data['lokasi']

            pengaduan.judul = judul
            pengaduan.isi = isi
            pengaduan.lokasi = lokasi
            pengaduan.save()
            return Response(serializer.data, status=HttpStatus.HTTP_200_OK)
        
        if pengaduan.user.is_superuser :
            status = request.data['status']
            pengaduan.status = status
            pengaduan.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({'error_message' : 'Status bukan UNRESOLVED'}, status=HttpStatus.HTTP_403_FORBIDDEN)

    def delete(self, request, pk=None) :
        pengaduan = get_object_or_404(self.queryset, pk=pk)

        if pengaduan.Status.UNRESOLVED :
            pengaduan.delete()
            return Response(status=HttpStatus.HTTP_200_OK)
        
        return Response({'error_message' : 'Status bukan UNRESOLVED'}, status=HttpStatus.HTTP_403_FORBIDDEN)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()