from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from jwt.lib import sso_authenticated
from .models import Image, Video
from .serializers import *

CLOUD_NAME = "[ISI DENGAN CLOUD NAME]"

# Create your views here.
class CloudinaryImageGetCreate(APIView):
  @sso_authenticated
  def get(self, request, id=None):
    if id is None:
      images = Image.objects.all()
      for image in images:
        image.image_url = "https://res.cloudinary.com/" + CLOUD_NAME + "/" + str(image.image_url)

      serializer = ImageGetSerializer(images, many=True)
      return Response(
        {
          'message': 'Image ditemukan',
          'data': {
            'images': serializer.data
          }
        }, 
        status=status.HTTP_200_OK
      )
    else:
      try:
        image = Image.objects.get(uuid=id)
        image.image_url  = "https://res.cloudinary.com/" + CLOUD_NAME + "/" + str(image.image_url)
        serializer = ImageGetSerializer(image, many=False)
        return Response(
          {
            'message': 'Image ditemukan',
            'data': {
              'image': serializer.data
            }
          }, 
          status=status.HTTP_200_OK
        )
      except Image.DoesNotExist:
        return Response({'error_message': 'Image tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

  @sso_authenticated
  def post(self, request):
    sso_user = request.sso_user
    if sso_user is None:
      return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = ImagePostSerializer(data=request.data)
    if serializer.is_valid():
      newImage = serializer.save(owner=sso_user)
      return Response(ImagePostSerializer(newImage).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @sso_authenticated
  def delete(self, request):
    images = Image.objects.all()
    for image in images:
      image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

class CloudinaryVideoGetCreate(APIView):
  @sso_authenticated
  def get(self, request, id=None):
    if id is None:
      videos = Video.objects.all()
      for video in videos:
        video.video_url = "https://res.cloudinary.com/" + CLOUD_NAME +"/" + str(video.video_url)

      serializer = VideoGetSerializer(videos, many=True)
      return Response(
        {
          'message': 'Image ditemukan',
          'data': {
            'images': serializer.data
          }
        },
        status=status.HTTP_200_OK
      )
    else:
      try:
        video = Video.objects.get(uuid=id)
        serializer = VideoGetSerializer(video)
        return Response(
          {
            'message': 'Image ditemukan',
            'data': {
              'image': serializer.data
            }
          }, 
          status=status.HTTP_200_OK
        )
      except Video.DoesNotExist:
        return Response({'error_message': 'Video tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

  @sso_authenticated
  def post(self, request):
    sso_user = request.sso_user
    if sso_user is None:
      return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = VideoPostSerializer(data=request.data)
    if serializer.is_valid():
      newVideo = serializer.save(owner=sso_user)
      return Response(VideoPostSerializer(newVideo).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)