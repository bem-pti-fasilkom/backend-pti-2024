from django.db import models

class SSOAccount(models.Model):
    npm = models.CharField(max_length=255, primary_key=True)
    full_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    faculty = models.CharField(max_length=255)
    short_faculty = models.CharField(max_length=255)
    major = models.CharField(max_length=255)
    program = models.CharField(max_length=255)

    def __str__(self):
        return self.username