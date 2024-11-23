from django.db import models

# Create your models here.
class Event(models.Model):
    img_url = models.CharField(max_length=255)
    biro_name = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.event_name