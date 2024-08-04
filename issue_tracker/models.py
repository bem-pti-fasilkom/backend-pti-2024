from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User


# TODO: Buat sistem history update status pengaduan
class Pengaduan(models.Model):
    class Status(models.TextChoices):
        UNRESOLVED = "U", _("Unresolved")
        RESOLVED = "RS", _("Resolved")
        REPORTED = "RP", _("Reported")

    anonymous = models.BooleanField()

    # TODO: Gunakan model user SSO
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pengaduan", null=True
    )

    judul = models.CharField(max_length=100)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.UNRESOLVED
    )
    isi = models.TextField()
    lokasi = models.TextField(null=True)
    evidence = models.URLField(null=True)
    tanggal_post = models.DateTimeField(auto_now=True)


class Like(models.Model):
    # TODO: Gunakan model user SSO
    akun_sso = models.URLField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )


class Comment(models.Model):
    # TODO: Gunakan model user SSO
    author = models.CharField(max_length=100, null=True, blank=True)
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )
