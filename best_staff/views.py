from .serializers import BEMMemberSerializer, EventSerializer, BirdeptSerializer, AllStatisticsOut, VoteCreateOut, VoteStatsOut, AllWinnersOutSerializer
from .models import BEMMember, Event, Birdept, Vote
from jwt.lib import sso_authenticated, SSOAccount
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.db.models import Count
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from django.views.decorators.csrf import csrf_exempt

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
        bem_member = BEMMember.objects.get(sso_account=request.sso_user)
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
        current_user = BEMMember.objects.get(sso_account=request.sso_user)    
    except Exception:
        return Response({'error_message': 'Anda bukan staff BEM'}, status=status.HTTP_403_FORBIDDEN)
    
    if current_user.role == 'KOOR':
        members = (
            BEMMember.objects
            .filter(role='STAFF')
            .exclude(pk=current_user.pk)
            .distinct()
        )
    else:
        members = (
            BEMMember.objects
            .filter(
                birdept__in=current_user.birdept.all(),
                role='STAFF'
            )
            .exclude(pk=current_user.pk)
            .distinct()
        )

    members = list(members)

    members.sort(
        key=lambda m: (
            list(m.birdept.values_list('nama', flat=True))[0]
            if m.birdept.exists()
            else ''
        )
    )

    return Response(BEMMemberSerializer(members, many=True).data)


@extend_schema(
    operation_id="best_staff_statistics_all",
    parameters=[
        OpenApiParameter(
            name="year",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.INT,
        ),
        OpenApiParameter(
            name="month",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.INT,
        ),
    ],
    responses={
        200: AllStatisticsOut,
        400: OpenApiResponse(description="Invalid year/month"),
    },
)
@api_view(["GET"])
@sso_authenticated
def get_all_statistics(request):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    votes = Vote.objects.all()

    if year and month:
        try:
            votes = votes.filter(created_at__year=int(year), created_at__month=int(month))
        except ValueError:
            return Response(
                {"error_message": "year dan month harus berupa integer positif"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        now = datetime.now()
        votes = votes.filter(created_at__year=now.year, created_at__month=now.month)

    birdepts = Birdept.objects.all()

    responses = {
        "birdepts": [
            {
                "name": birdept.nama,
                "votes": [
                    {
                        "name": member.sso_account.full_name,
                        "count": votes.filter(voted=member).count(),
                        "img_url": member.img_url,
                    }
                    for member in BEMMember.objects.filter(birdept=birdept)
                ],
            }
            for birdept in birdepts
        ]
    }

    return Response(responses)


@extend_schema(
    operation_id="best_staff_vote_statistics",
    parameters=[
        OpenApiParameter(
            name="birdept",
            location=OpenApiParameter.PATH,
            required=True,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="year",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.INT,
        ),
        OpenApiParameter(
            name="month",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.INT,
        ),
    ],
    responses={
        200: VoteStatsOut,
        400: OpenApiResponse(description="Invalid year/month"),
        401: OpenApiResponse(description="Unauthorized"),
        404: OpenApiResponse(description="Birdept tidak ditemukan"),
    },
)
@api_view(["GET"])
@sso_authenticated
def get_statistic(request, birdept):
    year = request.query_params.get("year")
    month = request.query_params.get("month")

    try:
        Birdept.objects.get(nama__iexact=birdept)
    except Birdept.DoesNotExist:
        return Response({'error_message': 'Birdept tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)

    birdept = Birdept.objects.get(nama__iexact=birdept)
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
                    "count": votes.filter(voted=m).count(),
                    "img_url": m.img_url,
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
            "img_url": m.img_url,
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
    birdept = Birdept.objects.all()
    serializer = BirdeptSerializer(birdept, many=True)
    return Response(serializer.data)


@extend_schema(
    operation_id="best_staff_vote_create",
    request=None,
    parameters=[
        OpenApiParameter(
            name="voted_npm",
            location=OpenApiParameter.PATH,
            required=True,
            type=OpenApiTypes.STR,
        ),
    ],
    responses={
        201: VoteCreateOut,
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
    },
)
@csrf_exempt
@sso_authenticated
@api_view(["POST"])
def create_vote(request, voted_npm): 
    voter = BEMMember.objects.get(sso_account=request.sso_user)

    # handle just in case votednya bukan anggota BEM
    try:
        voted = BEMMember.objects.get(pk=voted_npm)
    except BEMMember.DoesNotExist:
        return Response({'error_message': 'NPM tidak terdaftar sebagai anggota BEM'}, status=status.HTTP_403_FORBIDDEN)

    if (voter.pk == voted_npm):
        return Response({'error_message': 'Tidak bisa vote diri sendiri'}, status=status.HTTP_403_FORBIDDEN)

    if voted.role != "STAFF":
        return Response(
            {'error_message': 'Vote hanya bisa diberikan kepada STAFF'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    voter_birdept = voter.birdept.all()
    voted_birdept = voted.birdept.all()

    # BPH & STAFF: hanya boleh vote 1 staff di birdept sendiri
    if voter.role in ["BPH", "STAFF"]:
        if not set(voter_birdept).intersection(voted_birdept):
            return Response(
                {'error_message': 'Anda hanya bisa vote staff di birdept sendiri'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if Vote.objects.filter(voter=voter).exists():
            return Response(
                {'error_message': 'Anda hanya bisa vote satu kali'},
                status=status.HTTP_403_FORBIDDEN
            )

   # KOOR: boleh lintas birdept, tapi max 1 per birdept
    if voter.role == "KOOR":
        voted_birdept_id = voted.birdept.first().id

        if Vote.objects.filter(
            voter=voter,
            birdept_id=voted_birdept_id
        ).exists():
            return Response(
                {'error_message': 'Anda sudah vote staff di birdept ini'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    vote = Vote.objects.create(
        voter=voter,
        voted=voted,
        birdept_id=voted.birdept.first().id
    )

    return Response(
        {
            'message': 'Vote berhasil',
            'payload': {
                'voted_name': voted.sso_account.full_name,
                'birdept': voted.birdept.first().nama,
                'timestamp': vote.created_at
            }
        }, 
        status=status.HTTP_201_CREATED
    )