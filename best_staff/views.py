from django.shortcuts import render
from .serializers import BEMMemberSerializer, EventSerializer
from .models import BEMMember, Event
from jwt.lib import sso_authenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view

# Create your views here.
@sso_authenticated
@api_view(['GET'])
def authenticate_staff(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    npm = request.sso_user.get('npm')
    try:
        bem_member = BEMMember.objects.get(npm=npm)
        serializer = BEMMemberSerializer(bem_member)
        return Response(serializer.data)
    except BEMMember.DoesNotExist:
        return Response({'error_message': 'Anda bukan staff BEM'}, status=status.HTTP_403_FORBIDDEN)

@sso_authenticated
@api_view(['GET'])
def get_event(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)