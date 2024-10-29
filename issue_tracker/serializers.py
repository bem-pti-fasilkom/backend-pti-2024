from .models import SSOAccount, Pengaduan, Like, Comment
from rest_framework import serializers


class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = ["username", "npm", "full_name", "faculty", "short_faculty", "major", "program"]


class PengaduanSerializer(serializers.ModelSerializer):
    like_count = Pengaduan.objects.prefetch_related("issue_tracker_like").count()
    author = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return LikeSerializer(obj.likes.all(), many=True).data

    def get_author(self, obj):
        if obj.is_anonymous:
            return None
        return SSOAccountSerializer(obj.author).data

    class Meta:
        model = Pengaduan
        read_only_fields = ["jumlah_like", "jumlah_komentar", "author", "status", "likes"]
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
            "author",
            "likes",
        ]

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            request = self.context.get('request', None)
            if request and request.method == 'GET' and 'pk' in request.parser_context['kwargs']:
                representation['comments'] = self.get_comments(instance)
            return representation
        
class SinglePengaduanSerializer(PengaduanSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        return CommentSerializer(obj.comments.all(), many=True).data

    class Meta:
        model = Pengaduan
        read_only_fields = ["jumlah_like", "jumlah_komentar", "author", "status", "likes"]
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
            "author",
            "likes",
            "comments",
        ]



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ["id", "akun_sso", "pengaduan"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author", "isi", "pengaduan"]
