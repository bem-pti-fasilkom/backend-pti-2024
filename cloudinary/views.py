from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from jwt.lib import sso_authenticated
from .models import Image, Video
from .serializers import ImageSerializer, VideoSerializer

KEY = "Secret key django di sini"

# Create your views here.
class CloudinaryImageGetCreate(APIView):
  @sso_authenticated
  def get(self, request, id=None):
    if id is None:
      images = Image.objects.all()
      for image in images:
        image.url = "https://res.cloudinary.com/" + KEY + "/" + image.url

      return Response(
        {
          'message': 'Image ditemukan',
          'data': {
            'images': images
          }
        }, 
        status=status.HTTP_200_OK
      )
    else:
      try:
        image = Image.objects.get(id=id)

        return Response(
          {
            'message': 'Image ditemukan',
            'data': {
              'image': image
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
    
    serializer = ImageSerializer(data=request.data)
    if serializer.is_valid():
      newImage = serializer.save(owner=sso_user)
      return Response(ImageSerializer(newImage).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CloudinaryVideoGetCreate(APIView):
  @sso_authenticated
  def get(self, request, id=None):
    if id is None:
      videos = Video.objects.all()
      for video in videos:
        video.url = "https://res.cloudinary.com/" + KEY + "/" + video.url

      return Response(
        {
          'message': 'Video ditemukan',
          'data': {
            'videos': videos
          }
        }, 
        status=status.HTTP_200_OK
      )
    else:
      try:
        video = Video.objects.get(id=id)

        return Response(
          {
            'message': 'Video ditemukan',
            'data': {
              'video': video
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
    
    serializer = VideoSerializer(data=request.data)
    if serializer.is_valid():
      newVideo = serializer.save(owner=sso_user)
      return Response(VideoSerializer(newVideo).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)