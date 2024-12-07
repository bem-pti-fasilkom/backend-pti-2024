# Generated by Django 5.1 on 2024-11-17 16:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issue_tracker', '0010_comment_tanggal_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='PengaduanStatusChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=10)),
                ('tanggal', models.DateTimeField(default=django.utils.timezone.now)),
                ('pengaduan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_changes', to='issue_tracker.pengaduan')),
            ],
        ),
    ]