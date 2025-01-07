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

@api_view(['GET'])
def get_event(_):
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
        print(birdept.pk)
        birdept_members = BEMMember.objects.filter(birdept=birdept.pk).exclude(sso_account=current_user.sso_account)

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
    voter_sso = SSOAccount.objects.get(username=request.sso_user)
    voter = BEMMember.objects.get(npm=voter_sso.npm)

    # handle just in case votednya bukan anggota BEM
    try:
        voted = BEMMember.objects.get(npm=voted_npm)
    except BEMMember.DoesNotExist:
        return Response({'error_message': 'NPM tidak terdaftar sebagai anggota BEM'}, status=status.HTTP_403_FORBIDDEN)

    if (voter.npm == voted_npm):
        return Response({'error_message': 'Tidak bisa vote diri sendiri'}, status=status.HTTP_403_FORBIDDEN)
    
    # assign vote type
    if (voted.role == "KOOR"):
        vote_type = "PI"
    elif (voted.role == "BPH" or voted.role == "STAFF"):
        vote_type = "STAFF"

    # cek apakah voter sudah pernah vote dengan tipe itu atau belum (1 tipe 1 kali vote)
    if (Vote.objects.get(voter=voter, vote_type=vote_type, voted_npm=voted_npm).exists()):
        return Response({'error_message': 'Anda sudah vote'}, status=status.HTTP_403_FORBIDDEN)
        
    vote = Vote.objects.create(voter=voter, vote_type=vote_type, voted=voted)

    return Response(
            {
                'message': 'Vote berhasil',
                'data': {
                    'vote_type': vote_type,
                    'voted_name': voted.sso_account.full_name,
                    'timestamp': vote.created_at
                }
            }, 
            status=status.HTTP_201_CREATED
    )

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