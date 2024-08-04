from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]


class PengaduanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        # TODO: Sinkronisasi dengan model Pengaduan
        fields = [
            "id",
            "anonymous",
            "user",
            "judul",
            "status",
            "isi",
            "lokasi",
            "tanggal_post",
        ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        # TODO: Sinkronisasi dengan model Like
        fields = ["id", "user", "pengaduan"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # TODO: Sinkronisasi dengan model Comment
        fields = ["id", "user", "isi", "pengaduan"]
