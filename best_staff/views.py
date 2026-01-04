from .serializers import BEMMemberSerializer, EventSerializer, BirdeptSerializer, AllStatisticsOut, AllWinnersOutSerializer, WinnerSerializer
from .models import BEMMember, Event, Birdept, Vote, Winner
from jwt.lib import sso_authenticated, SSOAccount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Count
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@extend_schema(
    operation_id="best_staff_authenticate",
    responses={
        200: BEMMemberSerializer,
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden")
    },
)
@api_view(['GET'])
@sso_authenticated
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
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
    },
)
@api_view(['GET'])
@sso_authenticated
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

@api_view(["GET"])
@sso_authenticated
def get_statistic(request, birdept):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    try:
        Birdept.objects.get(nama=birdept)
    except Birdept.DoesNotExist:
        return Response({'error_message': 'Birdept tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

    birdept = Birdept.objects.get(nama=birdept)
    votes = Vote.objects.filter(birdept=birdept)

    if year and month:
        try:
            votes = votes.filter(created_at__year=int(year), created_at__month=int(month))
        except ValueError:
            return Response({"error_message": "year dan month harus berupa integer positif"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        now = datetime.now()
        votes = votes.filter(created_at__year=now.year, created_at__month=now.month)
    
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

@extend_schema(
    operation_id="best_staff_winners",
    parameters=[
        OpenApiParameter(name="year",  location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT),
        OpenApiParameter(name="month", location=OpenApiParameter.QUERY, required=False, type=OpenApiTypes.INT),
    ],
    responses={200: AllWinnersOutSerializer, 400: OpenApiResponse(description="Invalid year/month"), 401: OpenApiResponse(description="Unauthorized")},
)
@api_view(['GET'])
@sso_authenticated
def get_all_winners(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    qs = Vote.objects.all()
    if year and month:
        try:
            qs = qs.filter(created_at__year=int(year), created_at__month=int(month))
        except ValueError:
            return Response({"error_message": "year dan month harus berupa integer positif"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        now = datetime.now()
        qs = qs.filter(created_at__year=now.year, created_at__month=now.month)

    counts = qs.values("birdept_id", "voted_id").annotate(votes=Count("id")).order_by("-votes") # list voted tiap birdept

    totals = dict(qs.values("birdept_id").annotate(total=Count("id")).values_list("birdept_id", "total")) # total votes tiap birdept

    result = {}
    for row in counts:
        b_id = row["birdept_id"]
        m_id = row["voted_id"]
        c = row["votes"]

        if b_id not in result:
            result[b_id] = {"top": c, "winners": [m_id]}
        else:
            if c > result[b_id]["top"]:
                result[b_id] = {"top": c, "winners": [m_id]}
            elif c == result[b_id]["top"]:
                result[b_id]["winners"].append(m_id)


    bir_map = dict(Birdept.objects.values_list("id", "nama"))
    mem_map = {
        m.pk: {
            "npm": m.pk,
            "name": m.sso_account.full_name,
        }
        for m in BEMMember.objects.select_related("sso_account")
    }

    data = []
    for b_id, info in result.items():
        winners = [
            {
                **mem_map.get(m_id, {"npm": None, "name": "(unknown)"}),
                "votes": info["top"],
            }
            for m_id in info["winners"]
        ]
        data.append({
            "birdept_id": b_id,
            "birdept": bir_map.get(b_id, f"#{b_id}"),
            "total_votes": totals.get(b_id, 0),
            "top_votes": info["top"],
            "tie": len(winners) > 1,
            "winners": winners,
        })

    data.sort(key=lambda x: (x["birdept"] or ""))

    return Response({
        "filters": {"year": year, "month": month},
        "count": len(data),
        "results": data
    })

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

@sso_authenticated
@api_view(["POST"])
def create_vote(request, voted_npm): 
    # get voter (BEMMember) object
    voter_sso = SSOAccount.objects.get(username=request.sso_user)
    voter = BEMMember.objects.get(sso_account=voter_sso.npm)

    # handle just in case votednya bukan anggota BEM
    try:
        voted = BEMMember.objects.get(sso_account=voted_npm)
    except BEMMember.DoesNotExist:
        return Response({'error_message': 'NPM tidak terdaftar sebagai anggota BEM'}, status=status.HTTP_403_FORBIDDEN)

    voter_birdept = voter.birdept.all()
    voted_birdept = voted.birdept.all()

    if (voter.pk == voted_npm):
        return Response({'error_message': 'Tidak bisa vote diri sendiri'}, status=status.HTTP_403_FORBIDDEN)

    if voter.role != "KOOR" and voted.role == "KOOR":
        return Response({'error_message': 'Anda tidak bisa vote koorbid'}, status=status.HTTP_403_FORBIDDEN)

    if not set(voter_birdept).intersection(voted_birdept):
        return Response({'error_message': 'Anda tidak bisa vote anggota birdept lain'}, status=status.HTTP_403_FORBIDDEN)

    all_votes = Vote.objects.filter(voter=voter)
    all_vote_birdept_ids = all_votes.values_list("birdept", flat=True)
    voter_birdept_ids = voter.birdept.all().values_list("id", flat=True)
    if len(voter_birdept_ids.difference(all_vote_birdept_ids)) == 0:
        return Response({'error_message': 'Anda sudah vote di seluruh birdept'}, status=status.HTTP_403_FORBIDDEN)

    if voted.role != "KOOR" and len(Vote.objects.filter(voter=voter, birdept_id__in=[voted.birdept.first()])) > 0:
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
            'payload': {
                'voted_name': voted.sso_account.full_name,
                    'timestamp': vote.created_at
                }
        }, 
        status=status.HTTP_201_CREATED
    )

@api_view(["GET"])
def get_valid_winners(request):
    year = request.GET.get("year")
    month = request.GET.get("month")

    valid_winners = Winner.objects.filter(year=year, month=month)
    serializer = WinnerSerializer(valid_winners, many=True)
    data = serializer.data

    for i in range(len(data)):
        bem_member = valid_winners[i].member
        sso_account = bem_member.sso_account
        member = {
            'nama': sso_account.full_name,
            'jurusan': sso_account.major,
            'angkatan': '20'+sso_account.npm[:2],
            'birdept': bem_member.birdept.first().nama,
            'img_url': bem_member.img_url
        }
        data[i]['member'] = member

    return Response(
        {
            'data': data
        },
        status=status.HTTP_200_OK
    )