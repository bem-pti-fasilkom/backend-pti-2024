from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Event(models.Model):
    class Biro(models.TextChoices):
        ADKESMA = "ADKESMA", _("Advokasi Kesejahteraan Mahasiswa")
        BISMIT = "BISMIT", _("Bisnis dan Kemitraan")
        HUMAS = "HUMAS", _("Hubungan Masyarakat")
        KASTRAT = "KASTRAT", _("Kajian dan Aksi Strategis")
        MEDIA = "MEDIA", _("Media")
        DEPOR  = "DEPOR", _("Olahraga")
        PENGMAS = "PENGMAS", _("Pengabdian Masyarakat")
        PKKM = "PKKM", _("Pengembangan Karier dan Keilmuan Mahasiswa")
        PSDM = "PSDM", _("Pengembangan Sumber Daya Manusia")
        PTI = "PTI", _("Pengembangan Teknologi Informasi")
        SENBUD = "SENBUD", _("Seni dan Budaya")

    img_url = models.CharField(max_length=255)
    biro_name = models.CharField(max_length=255, choices=Biro.choices)
    event_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.event_name