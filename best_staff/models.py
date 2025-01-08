from django.db import models
from django.utils import timezone
from jwt.lib import SSOAccount

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
    
    npm = models.ForeignKey(
        'NPM_Whitelist',
        on_delete = models.CASCADE,
        null = True,
        blank = True
    )

    birdept = models.ForeignKey(
        'Birdept',
        on_delete = models.CASCADE,
        null = True,
        blank = True
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
    
class NPM_Whitelist(models.Model):
    npm = models.CharField(max_length=10, primary_key=True)
    birdept = models.ForeignKey(Birdept, on_delete=models.CASCADE, related_name='npm_whitelists')
    
    def __str__(self):
        return self.npm
    
class Vote(models.Model):
    # Voter can vote for PI or BPH
    voter = models.ForeignKey(BEMMember, on_delete=models.CASCADE)
    voted = models.ForeignKey(BEMMember, on_delete=models.CASCADE, related_name='voted')
    birdept = models.ForeignKey(Birdept, on_delete=models.CASCADE)
    
    class vote_type(models.TextChoices):
        PI = "PI", _("PI")
        STAFF = "STAFF", _("STAFF")

    created_at = models.DateTimeField(editable=True, default=timezone.now)
    
