from django.db import models
from django.utils import timezone
from jwt.lib import SSOAccount
from django.utils.translation import gettext_lazy as _

# Create your models here.
class BEMMember(models.Model):
    sso_account = models.OneToOneField(
        SSOAccount,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    
    class Role(models.TextChoices):
        STAFF = "STAFF"
        BPH = "BPH"
        KOOR = "KOOR"
    
    role = models.CharField(
        max_length = 5, choices = Role.choices, default = Role.STAFF
    )
    
    img_url = models.URLField()

    birdept = models.ManyToManyField(
        'Birdept',
        blank=True
    )
    
class Event(models.Model):
    start = models.DateTimeField(editable=True, default=timezone.now)
    end = models.DateTimeField(editable=True, default=timezone.now)

    def __str__(self):
        return self.start.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + self.end.strftime('%Y-%m-%d %H:%M:%S')

class Birdept(models.Model):
    nama = models.CharField(max_length=100)
    desc = models.CharField(max_length=100)
    galeri = models.JSONField(default=list)

    def __str__(self):
        return self.nama

    
class Vote(models.Model):
    # Voter can vote for PI or BPH
    voter = models.ForeignKey(BEMMember, on_delete=models.CASCADE)
    voted = models.ForeignKey(BEMMember, on_delete=models.CASCADE, related_name='voted')
    birdept = models.ForeignKey(Birdept, on_delete=models.CASCADE)

    def __str__(self):
        return self.voter.sso_account.full_name + ' voted ' + self.voted.sso_account.full_name

    created_at = models.DateTimeField(editable=True, default=timezone.now)
    
