from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import User


class Pengaduan(models.Model):
    class Status(models.TextChoices):
        UNRESOLVED = "U", _("Unresolved")
        RESOLVED = "RS", _("Resolved")
        REPORTED = "RP", _("Reported")

    anonymous = models.BooleanField()

    # TODO: Let user be identified by SSO account
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="pengaduan", null=True, blank=False
    )

    judul = models.CharField(max_length=100)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.UNRESOLVED
    )
    isi = models.TextField()
    lokasi = models.TextField()
    tanggal_post = models.DateTimeField(auto_now=True)


class Like(models.Model):
    akun_sso = models.URLField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )


class Comment(models.Model):
    author = models.CharField(max_length=100, null=True, blank=True)
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )
