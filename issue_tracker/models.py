from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User


class Pengaduan(models.Model):

    anonymous = models.BooleanField()

    npm = models.CharField(max_length=10)
    judul = models.CharField(max_length=100)
    isi = models.TextField()
    lokasi = models.TextField(null=True)
    evidence = models.URLField(null=True)
    tanggal_post = models.DateTimeField(auto_now=True)


class Like(models.Model):
    npm = models.CharField(max_length=10)
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )


class Comment(models.Model):
    npm = models.CharField(max_length=10, null=True, blank=True)
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )


# TODO: Buat sistem history update status pengaduan
class StatusUpdate(models.Model):
    class Status(models.TextChoices):
        UNRESOLVED = "U", _("Unresolved")
        RESOLVED = "RS", _("Resolved")
        REPORTED = "RP", _("Reported")

    status = models.CharField(choices=Status.choices, max_length=2)
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="status_updates"
    )
    comment = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
