from rest_framework import serializers
from .models import Image, Video

class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

class VideoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['video']

class ImageGetSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = ['uuid', 'image']

    def get_image(self, obj):
        return obj.image.url

class VideoGetSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['uuid', 'video']

    def get_video(self, obj):
        return obj.video.url
