# Generated by Django 5.1 on 2024-09-12 06:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0004_alter_pengaduan_tanggal_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pengaduan',
            name='tanggal_post',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
