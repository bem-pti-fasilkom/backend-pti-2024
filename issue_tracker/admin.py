from django.contrib import admin
from .models import Pengaduan, Like, PengaduanStatusChange, Comment


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
    
    # on update pengaduan status
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Pengaduan.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                change = PengaduanStatusChange.objects.create(pengaduan=obj, old_status=old_obj.status, new_status=obj.status, admin=request.user)
                change.save()
        super().save_model(request, obj, form, change)
    
class LikeModelAdmin(admin.ModelAdmin):
    verbose_name = "Like"
    def get_fields(self, _, obj=None):
        return [
            "akun_sso",
            "pengaduan",
        ]
    
class PengaduanStatusChangeModelAdmin(admin.ModelAdmin):
    verbose_name = "Pengaduan Status Change"
    def get_fields(self, _, obj=None):
        return [
            "pengaduan",
            "old_status",
            "new_status",
            "admin",
            "tanggal",
        ]
    
class CommentModelAdmin(admin.ModelAdmin):
    verbose_name = "Comment"
    def get_fields(self, _, obj=None):
        return [
            "author",
            "isi",
            "pengaduan",
            "tanggal_post",
        ]


admin.site.register(Pengaduan, PengaduanModelAdmin)
admin.site.register(Like, LikeModelAdmin)
admin.site.register(PengaduanStatusChange, PengaduanStatusChangeModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
