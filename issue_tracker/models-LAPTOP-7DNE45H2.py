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

class StatusPengaduan(models.Model) :
    class Status(models.TextChoices) :
        UNRESOLVED = "U", _("Unresolved")
        RESOLVED = "RS", _("Resolved")
        REPORTED = "RP", _("Reported")
    
    pengaduan = models.ForeignKey(Pengaduan, on_delete=models.CASCADE, related_name='status_update')
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.UNRESOLVED)
    comment =  models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

class Like(models.Model):
    npm = models.CharField(max_length=10)
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="likes"
    )


class Comment(models.Model):
    anonymous = models.BooleanField()
    npm = models.CharField(max_length=10)
    isi = models.TextField()
    pengaduan = models.ForeignKey(
        Pengaduan, on_delete=models.CASCADE, related_name="comments"
    )
