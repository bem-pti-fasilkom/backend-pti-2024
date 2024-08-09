from django.contrib import admin
from .models import Pengaduan


class PengaduanModelAdmin(admin.ModelAdmin):
    list_display = [
        "anonymous",
        "npm",
        "judul",
        "isi",
        "lokasi",
        "tanggal_post",
    ]


admin.site.register(Pengaduan, PengaduanModelAdmin)
