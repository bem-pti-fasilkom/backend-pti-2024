# Generated by Django 5.1 on 2024-11-23 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_web', '0004_alter_event_biro_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='biro_name',
            field=models.CharField(choices=[('ADKESMA', 'Advokasi Kesejahteraan Mahasiswa'), ('BISMIT', 'Bisnis dan Kemitraan'), ('HUMAS', 'Hubungan Masyarakat'), ('KASTRAT', 'Kajian dan Aksi Strategis'), ('MEDIA', 'Media'), ('DEPOR', 'Olahraga'), ('PENGMAS', 'Pengabdian Masyarakat'), ('PKKM', 'Pengembangan Karier dan Keilmuan Mahasiswa'), ('PSDM', 'Pengembangan Sumber Daya Manusia'), ('PTI', 'Pengembangan Teknologi Informasi'), ('SENBUD', 'Seni dan Budaya'), ('SKI', 'Satuan Kontrol Internal')], max_length=255),
        ),
    ]
