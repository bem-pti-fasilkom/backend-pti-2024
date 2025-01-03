from django.shortcuts import render
from .serializers import BEMMemberSerializer, EventSerializer, SSOAccountSerializer, NPMWhitelistSerializer, BirdeptSerializer
from .models import BEMMember, Event, NPM_Whitelist, Birdept
from jwt.lib import sso_authenticated, SSOAccount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Create your views here.
@sso_authenticated
@api_view(['GET'])
def authenticate_staff(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    sso_account = SSOAccount.objects.get(username=request.sso_user)
    serializer = SSOAccountSerializer(sso_account)
    npm = serializer.data.get('npm')

    try:
        bem_member = BEMMember.objects.get(npm=npm)
        serializer = BEMMemberSerializer(bem_member)
        return Response(serializer.data)
    except Exception:
        return Response({'error_message': 'Anda bukan staff BEM'}, status=status.HTTP_403_FORBIDDEN)

@sso_authenticated
@api_view(['GET'])
def get_event(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)

@sso_authenticated
@api_view(['GET'])
def get_npm_whitelist(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    npm_whitelist = NPM_Whitelist.objects.all()
    serializer = NPMWhitelistSerializer(npm_whitelist, many=True)
    return Response(serializer.data)

@sso_authenticated
@api_view(['GET'])
def get_birdept(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    birdept = Birdept.objects.all()
    serializer = BirdeptSerializer(birdept, many=True)
    return Response(serializer.data)