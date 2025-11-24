from django.db import models
from cloudinary.models import CloudinaryField
from jwt.lib import SSOAccount
import uuid

class Image(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=True)
    owner = models.ForeignKey(SSOAccount, editable=False, null=False, on_delete=models.CASCADE)
    url = CloudinaryField('image')

class Video(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=True)
    owner = models.ForeignKey(SSOAccount, editable=False, null=False, on_delete=models.CASCADE)
    url = CloudinaryField('video')