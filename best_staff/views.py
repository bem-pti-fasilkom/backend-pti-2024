from .serializers import BEMMemberSerializer, EventSerializer, BirdeptSerializer, AllStatisticsOut, VoteCreateOut, VoteStatsOut
from .models import BEMMember, Event, Birdept, Vote
from jwt.lib import sso_authenticated, SSOAccount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

# Create your views here.
@extend_schema(
    operation_id="best_staff_authenticate",
    responses={
        200: BEMMemberSerializer,
        401: OpenApiResponse(description="Unauthorized"),
    },
)
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

@extend_schema(
    operation_id="best_staff_events_list",
    responses=EventSerializer(many=True),
)
@api_view(['GET'])
def get_event(_):
    event = Event.objects.all()
    serializer = EventSerializer(event, many=True)
    return Response(serializer.data)

@extend_schema(
    operation_id="best_staff_birdept_members",
    responses={
        200: BEMMemberSerializer(many=True),
        401: OpenApiResponse(description="Unauthenticated"),
        403: OpenApiResponse(description="Forbidden"),
    },
)
@sso_authenticated
@api_view(['GET'])
def get_birdept_member(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        if not isinstance(request.sso_user, SSOAccount):
            request.sso_user = SSOAccount.objects.get(username=request.sso_user["user"])

        current_user = BEMMember.objects.get(sso_account=request.sso_user)    
    except Exception:
        # Adjust Error msg for this one (no info mw dikasi error msg apa)
        return Response({'error_message': 'Anda bukan staff BEM'}, status=status.HTTP_403_FORBIDDEN)
    
    members = (
        BEMMember.objects
            .filter(birdept__in=current_user.birdept.all())
            .exclude(pk=current_user.pk)
            .distinct()
    )

    return Response(BEMMemberSerializer(members, many=True).data)

@extend_schema(
    operation_id="best_staff_statistics_all",
    responses=AllStatisticsOut,
)
@api_view(['GET'])
def get_all_statistics(_):
    birdepts = Birdept.objects.all()
    responses = {
        "birdepts": [
            {
                "name": birdept.nama,
                "votes": [
                    {
                        "name": m.sso_account.full_name,
                        "count": Vote.objects.filter(voted=m).count()
                    } for m in BEMMember.objects.filter(birdept=birdept)
                ]
            } for birdept in birdepts
        ]
    }

    return Response(responses)

@extend_schema(
    operation_id="best_staff_birdept_list",
    responses=BirdeptSerializer(many=True),
)
@api_view(['GET'])
def get_birdept(request):
    if request.sso_user is None:
        return Response({'error_message': 'Autentikasi Gagal'}, status=status.HTTP_401_UNAUTHORIZED)
    
    birdept = Birdept.objects.all()
    serializer = BirdeptSerializer(birdept, many=True)
    return Response(serializer.data)

class VoteAPIView(APIView):
    @extend_schema(
        operation_id="best_staff_vote_create",
        request=None,
        responses={
            201: VoteCreateOut, 
            401: OpenApiResponse(description="Unauthorized"), 
            403: OpenApiResponse(description="Forbidden")
        },
        parameters=[
            OpenApiParameter(name="voted_npm", location=OpenApiParameter.PATH, required=True, type=str),
        ],
    )
    @sso_authenticated
    def post(self, request, voted_npm): 
        # get voter (BEMMember) object
        voter_sso = SSOAccount.objects.get(username=request.sso_user)
        voter = BEMMember.objects.get(npm=voter_sso.npm)
        voted = BEMMember.objects.get(npm=voted_npm)
        voter_birdept = voter.birdept.all()
        voted_birdept = voted.birdept.all()


        # handle just in case votednya bukan anggota BEM
        try:
            voted = BEMMember.objects.get(npm=voted_npm)
        except BEMMember.DoesNotExist:
            return Response({'error_message': 'NPM tidak terdaftar sebagai anggota BEM'}, status=status.HTTP_403_FORBIDDEN)

        if (voter.pk == voted_npm):
            return Response({'error_message': 'Tidak bisa vote diri sendiri'}, status=status.HTTP_403_FORBIDDEN)
        
        if voter.role != "KOOR" and voted.role == "KOOR":
            return Response({'error_message': 'Anda tidak bisa vote koorbid'}, status=status.HTTP_403_FORBIDDEN)

        if not set(voter_birdept).intersection(voted_birdept):
            return Response({'error_message': 'Anda tidak bisa vote anggota birdept lain'}, status=status.HTTP_403_FORBIDDEN)
        
        all_votes = Vote.objects.filter(npm=voter.npm)
        all_vote_birdept_ids = all_votes.values_list("birdept", flat=True)
        voter_birdept_ids = voter.birdept.all().values_list("birdept", flat=True)
        if len(voter_birdept_ids.difference(all_vote_birdept_ids)) == 0:
            return Response({'error_message': 'Anda sudah vote di seluruh birdept'}, status=status.HTTP_403_FORBIDDEN)

        if voted.role != "KOOR" and len(Vote.objects.filter(voter=voter, birdept_id__in=voted.birdept.first())) > 0:
            return Response({'error_message': 'Anda sudah vote di birdept ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if voted.role == "KOOR" and len(Vote.objects.filter(voter=voter, voted__role="KOOR")) > 0:
            return Response({'error_message': 'Anda sudah vote di birdept ini'}, status=status.HTTP_403_FORBIDDEN)
        
        if voted.role == "KOOR":
            vote = Vote.objects.create(voter=voter, voted=voted, birdept_id=1)

        if voted.role != "KOOR":
            vote = Vote.objects.create(voter=voter, voted=voted, birdept_id=voted.birdept.first().id)  



        return Response(
                {
                    'message': 'Vote berhasil',
                    'data': {
                        'voted_name': voted.sso_account.full_name,
                        'timestamp': vote.created_at
                    }
                }, 
                status=status.HTTP_201_CREATED
        )

    @extend_schema(
        operation_id="best_staff_vote_statistics",
        responses=VoteStatsOut,
        parameters=[
            OpenApiParameter(name="birdept", location=OpenApiParameter.PATH, required=True, type=str),
        ],
    )
    @sso_authenticated
    def get(self, _, birdept):
        try:
            Birdept.objects.get(nama=birdept)
        except Birdept.DoesNotExist:
            return Response({'error_message': 'Birdept tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

        birdept = Birdept.objects.get(nama=birdept)
        votes = Vote.objects.filter(birdept=birdept)
        member = BEMMember.objects.filter(birdept=birdept)

        responses = {
            "total_votes": votes.count(),
            "votes": {
                "details": [
                    {
                        "name": m.sso_account.full_name,
                        "count": votes.filter(voted=m).count()
                    } for m in member
                ]
            }
        }

        return Response(responses)