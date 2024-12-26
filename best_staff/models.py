from django.db import models
from django.utils import timezone

# Create your models here.
class BEMMember(models.Model):
    class Role(models.TextChoices):
        STAFF = "STAFF"
        BPH = "BPH"
        KOOR = "KOOR"
    
    role = models.CharField(
        max_length = 5, choices = Role.choices, default = Role.STAFF
    )
    
    img_url = models.URLField()

class Event(models.Model):
    start = models.DateTimeField(editable=True, default=timezone.now)
    end = models.DateTimeField(editable=True)