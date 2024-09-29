from django.db import models

# Create your models here.
class Event(models.Model):
    event_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()