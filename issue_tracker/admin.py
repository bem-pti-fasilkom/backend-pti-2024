from django.contrib import admin
from .models import Pengaduan, Like


class PengaduanModelAdmin(admin.ModelAdmin):
    verbose_name = "Pengaduan"

    def get_fields(self, _, obj=None):
        fields = [
            "author",
            "is_anonymous",
            "judul",
            "status",
            "isi",
            "lokasi",
        ]
        if obj and obj.is_anonymous:
            fields.remove("author")
            return fields
        return fields
    
class LikeModelAdmin(admin.ModelAdmin):
    verbose_name = "Like"
    def get_fields(self, _, obj=None):
        return [
            "akun_sso",
            "pengaduan",
        ]


admin.site.register(Pengaduan, PengaduanModelAdmin)
admin.site.register(Like, LikeModelAdmin)
