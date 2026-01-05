from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from jwt.lib import sso_authenticated
from .models import Image, Video
from .serializers import ImageGetSerializer, ImagePostSerializer, VideoGetSerializer, VideoPostSerializer

# Create your views here.
class CloudinaryImageGetCreate(APIView):
  parser_classes = [MultiPartParser, FormParser]

  @sso_authenticated
  def get(self, request, id=None):
    sso_user = request.sso_user
    if sso_user is None:
      return Response(
        {
          'error_message': 'Autentikasi Gagal'
        }, 
        status=status.HTTP_401_UNAUTHORIZED
      )
    
    if id is None:
      images = Image.objects.filter(owner=sso_user)
      serializer = ImageGetSerializer(images, many=True)
      return Response(
        {
          'message': 'Image ditemukan',
          'data': {
            'images': serializer.data,
          }
        }, 
        status=status.HTTP_200_OK
      )
    else:
      try:
        image = Image.objects.get(uuid=id)
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
        return Response(
          {
            'error_message': 'Image tidak ditemukan'
          }, 
          status=status.HTTP_404_NOT_FOUND
        )

  @sso_authenticated
  def post(self, request):
    sso_user = request.sso_user
    if sso_user is None:
      return Response(
        {
          'error_message': 'Autentikasi Gagal'
        }, 
        status=status.HTTP_401_UNAUTHORIZED
      )
    
    serializer = ImagePostSerializer(data=request.data)
    if serializer.is_valid():
      newImage = serializer.save(owner=sso_user)
      return Response(ImageGetSerializer(newImage).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CloudinaryVideoGetCreate(APIView):
  parser_classes = [MultiPartParser, FormParser]

  @sso_authenticated
  def get(self, request, id=None):
    sso_user = request.sso_user
    if sso_user is None:
      return Response(
        {
          'error_message': 'Autentikasi Gagal'
        }, 
        status=status.HTTP_401_UNAUTHORIZED
      )
    
    if id is None:
      videos = Video.objects.filter(owner=sso_user)
      serializer = VideoGetSerializer(videos, many=True)
      return Response(
        {
          'message': 'Video ditemukan',
          'data': {
            'videos': serializer.data
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
            'message': 'Video ditemukan',
            'data': {
              'video': serializer.data
            }
          }, 
          status=status.HTTP_200_OK
        )
      except Video.DoesNotExist:
        return Response(
          {
            'error_message': 'Video tidak ditemukan'
          }, 
          status=status.HTTP_404_NOT_FOUND
        )

  @sso_authenticated
  def post(self, request):
    sso_user = request.sso_user
    if sso_user is None:
      return Response(
        {
          'error_message': 'Autentikasi Gagal'
        }, 
        status=status.HTTP_401_UNAUTHORIZED
      )
    
    serializer = VideoPostSerializer(data=request.data)
    if serializer.is_valid():
      newVideo = serializer.save(owner=sso_user)
      return Response(VideoGetSerializer(newVideo).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)