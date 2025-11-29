from .models import SSOAccount, Pengaduan, Like, Comment, Evidence, PengaduanStatusChange
from rest_framework import serializers


class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = ["username", "npm", "full_name", "faculty", "short_faculty", "major", "program"]


class PengaduanSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    evidence = serializers.SerializerMethodField()

    def get_evidence(self, obj):
        return EvidenceSerializer(obj.evidence.all(), many=True).data

    def get_likes(self, obj):
        return LikeSerializer(obj.likes.all(), many=True).data

    def get_author(self, obj):
        if obj.is_anonymous:
            return None
        return SSOAccountSerializer(obj.author).data

    class Meta:
        model = Pengaduan
        read_only_fields = ["jumlah_like", "jumlah_komentar", "author", "status", "likes", "evidence"]
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
            "evidence",
            "kategori"
        ]

        def to_representation(self, instance):
            representation = super().to_representation(instance)
            request = self.context.get('request', None)
            if request and request.method == 'GET' and 'pk' in request.parser_context['kwargs']:
                representation['comments'] = self.get_comments(instance)
            return representation
        
class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["id", "url", "pengaduan"]

class PengaduanStatusChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PengaduanStatusChange
        fields = ["id", "pengaduan", "old_status", "new_status", "admin", "tanggal"]
        read_only_fields = ["admin", "tanggal", "old_status", "new_status"]

class SinglePengaduanSerializer(PengaduanSerializer):
    comments = serializers.SerializerMethodField()
    status_changes = serializers.SerializerMethodField()

    def get_comments(self, obj):
        return CommentSerializer(obj.comments.all(), many=True).data
    
    def get_status_changes(self, obj):
        return PengaduanStatusChangeSerializer(obj.status_changes.all(), many=True).data

    class Meta:
        model = Pengaduan
        read_only_fields = ["jumlah_like", "jumlah_komentar", "author", "status", "likes", "evidence"]
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
            "evidence",
            "status_changes",
            "kategori"
        ]



class LikeSerializer(serializers.ModelSerializer):
    npm = serializers.CharField(source="akun_sso.npm", read_only=True)

    class Meta:
        model = Like
        fields = ["id", "npm", "pengaduan"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        read_only_fields = ["author", "pengaduan", "tanggal_post", "is_anonymous"]
        fields = ["id", "author", "isi", "pengaduan", "tanggal_post", "is_anonymous"]

    def get_author(self, obj):
        if obj.is_anonymous:
            return None
        return SSOAccountSerializer(obj.author).data
