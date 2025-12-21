from .models import BEMMember, Event, Birdept, Vote
from rest_framework import serializers
from jwt.models import SSOAccount

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["start", "end"]
        
class BirdeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Birdept
        fields = ["nama", "displayed_name", "deskripsi", "galeri"]

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["voter", "voted", "birdept", "created_at"]
        
class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = "__all__"

class BEMMemberSerializer(serializers.ModelSerializer):
    sso_account = SSOAccountSerializer()
    birdept = serializers.SerializerMethodField()
    has_voted = serializers.BooleanField()
    koor_voted_birdepts = serializers.ListField()
    
    class Meta:
        model = BEMMember
        fields = ["sso_account", "role", "img_url", "birdept", "has_voted", "koor_voted_birdepts"]

    def get_birdept(self, obj):
        return list(obj.birdept.values_list("nama", flat=True))

# tambahan serializer buat serialize output

class VoteCount(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()

class VoteStatsOut(serializers.Serializer):
    total_votes = serializers.IntegerField()
    votes = serializers.JSONField()

class AllStatisticsBirdept(serializers.Serializer):
    name = serializers.CharField()
    votes = VoteCount(many=True)

class AllStatisticsOut(serializers.Serializer):
    birdepts = AllStatisticsBirdept(many=True)

class VoteCreateOut(serializers.Serializer):
    message = serializers.CharField()
    payload = serializers.JSONField()  

class WinnerItemSerializer(serializers.Serializer):
    npm = serializers.CharField(allow_null=True)
    name = serializers.CharField()
    votes = serializers.IntegerField()

class WinnerRowSerializer(serializers.Serializer):
    birdept_id = serializers.IntegerField()
    birdept = serializers.CharField(allow_null=True)
    total_votes = serializers.IntegerField()
    top_votes = serializers.IntegerField()
    tie = serializers.BooleanField()
    winners = WinnerItemSerializer(many=True)

class AllWinnersOutSerializer(serializers.Serializer):
    class Filters(serializers.Serializer):
        year = serializers.CharField(allow_null=True, required=False)
        month = serializers.CharField(allow_null=True, required=False)

    filters = Filters()
    count = serializers.IntegerField()
    results = WinnerRowSerializer(many=True)