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

    user = models.CharField(max_length=600)
    judul = models.CharField(max_length=100)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.UNRESOLVED
    )
    isi = models.TextField()
    lokasi = models.TextField(null=True)
    evidence = models.URLField(null=True)
    tanggal_post = models.DateTimeField(auto_now=True)


class Like(models.Model):
    user = models.CharField(max_length=600)
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )


class Comment(models.Model):
    user = models.CharField(max_length=600, null=True, blank=True)
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )
