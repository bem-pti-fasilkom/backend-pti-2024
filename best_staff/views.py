from django.shortcuts import render
from .serializers import BEMMemberSerializer, EventSerializer, NPMWhitelistSerializer, BirdeptSerializer
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
    
    try:
        sso_account = SSOAccount.objects.get(username=request.sso_user)
        bem_member = BEMMember.objects.get(sso_account=sso_account)
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

@sso_authenticated
@api_view(['GET'])
def get_birdept_member(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        sso_account = SSOAccount.objects.get(username=request.sso_user)
        current_user = BEMMember.objects.get(sso_account=sso_account)
        birdept = current_user.birdept
        birdept_members = BEMMember.objects.filter(birdept=birdept).exclude(sso_account=current_user.sso_account)
        
        serializer = BEMMemberSerializer(birdept_members, many=True)
        return Response(serializer.data)
    
    except Exception:
        # Adjust Error msg for this one (no info mw dikasi error msg apa)
        return Response({'error_message': 'Anda bukan staff BEM'}, status=status.HTTP_403_FORBIDDEN)

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