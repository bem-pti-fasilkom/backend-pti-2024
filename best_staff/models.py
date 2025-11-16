import datetime

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

    role = models.CharField(max_length=5, choices=Role.choices, default=Role.STAFF)

    img_url = models.URLField()

    birdept = models.ManyToManyField(
        'Birdept',
        blank=True
    )

    @property
    def has_voted(self):
        """Returns whether the BEM member has voted this month"""
        today = datetime.date.today()
        return Vote.objects.filter(
            voter=self,
            created_at__year=today.year,
            created_at__month=today.month
        ).exists()

    @property
    def koor_voted_birdepts(self):
        """
        Returns a list of the Birdept objects a KOOR has voted for this month.
        Returns an empty list if the user is not a KOOR.
        """
        if self.role != self.Role.KOOR:
            return []
            
        this_month = datetime.date.today().month
        
        # Get all birdept IDs this KOOR has voted for this month
        # .distinct() ensures each birdept is only listed once
        birdept_ids = Vote.objects.filter(
            voter=self,
            created_at__month=this_month
        ).values_list('birdept', flat=True).distinct()
        
        # Return the birdept standard names
        return list(Birdept.objects.filter(id__in=birdept_ids).values_list("nama", flat=True))
    
class Event(models.Model):
    start = models.DateTimeField(editable=True, default=timezone.now)
    end = models.DateTimeField(editable=True, default=timezone.now)

    def __str__(self):
        return (
            self.start.strftime("%Y-%m-%d %H:%M:%S")
            + " - "
            + self.end.strftime("%Y-%m-%d %H:%M:%S")
        )


class Birdept(models.Model):
    nama = models.CharField(max_length=200)
    displayed_name = models.CharField(max_length=200, default="")
    deskripsi = models.CharField(max_length=1000, default="")
    galeri = models.JSONField(default=list)

    def __str__(self):
        return self.nama


class Vote(models.Model):
    # Voter can vote for PI or BPH
    voter = models.ForeignKey(BEMMember, on_delete=models.CASCADE)
    voted = models.ForeignKey(BEMMember, on_delete=models.CASCADE, related_name="voted")
    birdept = models.ForeignKey(Birdept, on_delete=models.CASCADE)

    def __str__(self):
        return (
            self.voter.sso_account.full_name
            + " voted "
            + self.voted.sso_account.full_name
        )

    created_at = models.DateTimeField(editable=True, default=timezone.now)
