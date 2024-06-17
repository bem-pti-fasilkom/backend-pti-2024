from django.contrib import admin
from .models import Pengaduan


class PengaduanModelAdmin(admin.ModelAdmin):
    list_display = [
        "anonymous",
        "user",
        "judul",
        "status",
        "isi",
        "lokasi",
        "tanggal_post",
    ]


admin.site.register(Pengaduan, PengaduanModelAdmin)
