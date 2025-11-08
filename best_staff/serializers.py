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
        fields = ["nama", "desc", "galeri"]

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
    
    class Meta:
        model = BEMMember
        fields = ["sso_account", "role", "img_url"]