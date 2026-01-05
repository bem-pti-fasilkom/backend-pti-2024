from rest_framework import serializers
from .models import Image, Video

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_url']

class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['video_url']

class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['uuid', 'image_url']

class VideoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['uuid', 'video_url']