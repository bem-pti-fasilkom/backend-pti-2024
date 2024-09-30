from .models import SSOAccount, Pengaduan, Like, Comment
from rest_framework import serializers


class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = ["username", "npm", "full_name", "faculty", "short_faculty", "major", "program"]


class PengaduanSerializer(serializers.ModelSerializer):
    like_count = Pengaduan.objects.prefetch_related("issue_tracker_like").count()
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        if obj.is_anonymous:
            return None
        return SSOAccountSerializer(obj.author).data

    class Meta:
        model = Pengaduan
        read_only_fields = ["jumlah_like", "jumlah_komentar", "author", "status"]
        fields = [
            "id",
            "is_anonymous",
            "judul",
            "isi",
            "lokasi",
            "tanggal_post",
            "jumlah_like",
            "jumlah_komentar",
            "status",
            "author"
        ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "akun_sso", "pengaduan"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "isi", "pengaduan"]
