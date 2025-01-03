# Generated by Django 5.1 on 2024-11-23 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_url', models.CharField(max_length=255)),
                ('event_name', models.CharField(max_length=255)),
                ('start_date', models.DateTimeField()),
                ('registration_deadline', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('location', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
    ]
