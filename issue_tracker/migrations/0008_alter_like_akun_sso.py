# Generated by Django 5.1 on 2024-09-29 17:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0007_remove_pengaduan_anonymous_pengaduan_is_anonymous'),
        ('jwt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='akun_sso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='jwt.ssoaccount'),
        ),
    ]