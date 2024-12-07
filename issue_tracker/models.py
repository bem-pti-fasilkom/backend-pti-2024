from django.db import models
from django.utils.translation import gettext_lazy as _
from jwt.models import SSOAccount
from django.utils import timezone
from django.contrib.auth.models import User

class PengaduanStatusChange(models.Model):
    pengaduan = models.ForeignKey(
        "Pengaduan", on_delete=models.CASCADE, related_name="status_changes"
    )
    old_status = models.CharField(max_length=10)
    new_status = models.CharField(max_length=10)
    tanggal = models.DateTimeField(editable=True, default=timezone.now)
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pengaduan_status_changes"
    )
    def __str__(self):
        return f"{self.pengaduan} status changed from {self.old_status} to {self.new_status} by {self.admin} at {self.tanggal}"


class Pengaduan(models.Model):
    class Status(models.TextChoices):
        UNRESOLVED = "UNRESOLVED", _("Unresolved")
        RESOLVED = "RESOLVED", _("Resolved")
        REPORTED = "REPORTED", _("Reported")

    class Kaget(models.TextChoices):
        FINANSIAL = "FINANSIAL", _("Finansial")
        KEKERASAN_SEKSUAL = "KEKERASAN_SEKSUAL", _("Kekerasan Seksual")
        FASILITAS = "FASILITAS", _("Fasilitas")
        AKADEMIS = "AKADEMIS", _("Akademis")
        LAINNYA = "LAINNYA", _("Lainnya")

    is_anonymous = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.judul} by {self.author if not self.is_anonymous else 'Anonymous'}"

    author = models.ForeignKey(
        SSOAccount, on_delete=models.CASCADE, related_name="pengaduan"
    )

    judul = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.UNRESOLVED
    )
    kategori = models.CharField(
        max_length=64, choices=Kaget.choices, default=Kaget.LAINNYA
    )
    isi = models.TextField()
    lokasi = models.TextField(blank=True)
    tanggal_post = models.DateTimeField(editable=True, default=timezone.now)
    
    @property
    def jumlah_like(self):
        return self.likes.count()
    
    @property
    def jumlah_komentar(self):
        return self.comments.count()
    
    @property
    def semua_komentar(self):
        return self.comments.all()

class Evidence(models.Model):
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="evidence"
    )
    url = models.URLField()

    def __str__(self):
        return f"Evidence for {self.pengaduan}"

class Like(models.Model):
    akun_sso = models.ForeignKey(
        SSOAccount, on_delete=models.CASCADE, related_name="likes"
    )
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )

    def __str__(self):
        return f"{self.akun_sso} likes {self.pengaduan}"


class Comment(models.Model):
    is_anonymous = models.BooleanField(
        default=False
    )
    author = models.ForeignKey(
        SSOAccount, on_delete=models.CASCADE, related_name="comments"
    )
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )
    tanggal_post = models.DateTimeField(editable=True, default=timezone.now)
    def __str__(self):
        return f"{self.author} comment on {self.pengaduan} at {self.tanggal_post}"
