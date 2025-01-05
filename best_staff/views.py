from django.shortcuts import render
from .serializers import BEMMemberSerializer, EventSerializer, SSOAccountSerializer, NPMWhitelistSerializer, BirdeptSerializer, VoteSerializer
from .models import BEMMember, Event, NPM_Whitelist, Birdept, Vote
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

@sso_authenticated
@api_view(['POST'])
def vote(request, voted_npm): 
    # get voter (BEMMember) object
    sso_account = SSOAccount.objects.get(username=request.sso_user)
    serializer = SSOAccountSerializer(sso_account)
    npm = serializer.data.get('npm')
    voter = BEMMember.objects.get(npm=npm)

    # handle just in case npm nya bukan anggota BEM
    try:
        voted = BEMMember.objects.get(npm=npm)
    except Exception:
        return Response({'error_message': 'NPM tidak terdaftar sebagai anggota BEM'}, status=status.HTTP_403_FORBIDDEN)

    if (voter == voted):
        return Response({'error_message': 'Tidak bisa vote diri sendiri'}, status=status.HTTP_403_FORBIDDEN)
    
    # assign vote type
    if (voted.role == "KOOR"):
        vote_type = "PI"
    elif (voted.role == "BPH" or voted.role == "STAFF"):
        vote_type = "STAFF"

    # cek apakah voter sudah pernah vote dengan tipe itu atau belum (1 tipe 1 kali vote)
    try:
        vote = Vote.objects.get(voter=voter, vote_type=vote_type, voted_npm=voted_npm)
        return Response({'error_message': 'Anda sudah vote'}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        vote = Vote(voter=voter, vote_type=vote_type, voted=voted)
        vote.save()

    return Response({'message': 'Vote berhasil'}, status=status.HTTP_201_CREATED)

@sso_authenticated
@api_view(['GET'])
# dengan asumsi 
def get_vote(request, birdept):
    birdept = Birdept.objects.get(nama=birdept)
    votes = Vote.objects.filter(birdept=birdept)
    birdept_pi = BEMMember.objects.filter(birdept=birdept, role="KOOR")
    birdept_staff = BEMMember.objects.filter(birdept=birdept, role="STAFF")
    birdept_bph = BEMMember.objects.filter(birdept=birdept, role="BPH")

    responses = {
        "total_votes": votes.count(),
        "pi_votes": {
            "details": [
                {
                    "name": pi.sso_account.full_name,
                    "count": votes.filter(voted=pi).count()
                } for pi in birdept_pi
            ],
            "total": votes.filter(vote_type="PI").count()
        },
        "staff_votes": {
            "details": [
                {
                    "name": staff.sso_account.full_name,
                    "count": votes.filter(voted=staff).count()
                } for staff in birdept_staff
            ],
            "total": votes.filter(vote_type="STAFF").count()
        },
        "bph_votes": {
            "details": [
                {
                    "name": bph.sso_account.full_name,
                    "count": votes.filter(voted=bph).count()
                } for bph in birdept_bph
            ],
            "total": votes.filter(vote_type="BPH").count()
        }
    }

    return Response(responses)