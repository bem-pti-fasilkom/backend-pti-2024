from .models import Event
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .serializers import EventSerializer
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = 'page_size'

# Create your views here.
class ReadEvent(APIView):
    def get(self, request):
        search_query = request.query_params.get('search')
        if search_query:
            events = Event.objects.filter(title__icontains=search_query)
        else:
            events = Event.objects.all()
        paginator = StandardResultsSetPagination()
        paginated_events = paginator.paginate_queryset(events, request)
        serializer = EventSerializer(paginated_events, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class ReadEventDetail(APIView):
    def get(self, request, id):
        event = Event.objects.get(pk=id)
        serializer = EventSerializer(event)
        return Response(serializer.data)