# Generated by Django 5.0.6 on 2024-06-15 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pengaduan',
            name='evidence',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='pengaduan',
            name='lokasi',
            field=models.TextField(null=True),
        ),
    ]
