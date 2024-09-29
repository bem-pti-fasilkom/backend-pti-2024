from .models import Pengaduan
from rest_framework import serializers

class PengaduanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengaduan
        fields = '__all__'