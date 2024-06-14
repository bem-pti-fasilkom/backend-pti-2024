from django.shortcuts import get_object_or_404
from .serializers import *

from rest_framework.response import Response
from rest_framework import viewsets, status


class PengaduanViewSet(viewsets.ModelViewSet):
    serializer_class = PengaduanSerializer
    queryset = Pengaduan.objects.all()

    def retrieve(self, request, pk=None):
        pengaduan = get_object_or_404(self.queryset, pk=pk)
        serializer = PengaduanSerializer(pengaduan)

        # If the user desires to stay anonymous, do not return user object
        if pengaduan.__getattribute__("anonymous"):
            pengaduan.__setattr__("user", None)
            pengaduan.save()

        ## Used to format datetime into a more readable format
        # unformatted_date = pengaduan.__getattribute__("tanggal_post")
        # pengaduan.__setattr__("tanggal_post", unformatted_date.strftime("%Y-%m-%d, %X"))

        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
