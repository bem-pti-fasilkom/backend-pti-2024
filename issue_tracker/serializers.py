from .models import *
from rest_framework import serializers

# User disini digunakan untuk admin
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class PengaduanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        # TODO: Sinkronisasi dengan model Pengaduan
        fields = [
            "id",
            "anonymous",
            "npm",
            "judul",
            "isi",
            "lokasi",
            "tanggal_post",
        ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        # TODO: Sinkronisasi dengan model Like
        fields = ["id", "npm", "pengaduan"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # TODO: Sinkronisasi dengan model Comment
        fields = ["id", "npm", "isi", "pengaduan"]
