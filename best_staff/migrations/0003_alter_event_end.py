# Generated by Django 5.1 on 2025-01-07 18:13

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('best_staff', '0002_birdept_bemmember_birdept_npm_whitelist_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
