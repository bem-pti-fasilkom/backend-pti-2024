from .models import BEMMember, Event, NPM_Whitelist, Birdept, Vote
from rest_framework import serializers
from jwt.lib import SSOAccount

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["start", "end"]
        
class NPMWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = NPM_Whitelist
        fields = ["npm", "birdept"]
        
class BirdeptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Birdept
        fields = ["nama", "desc", "galeri", "npm_whitelists"]

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["voter", "voted", "vote_type", "created_at"]
        
class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = "__all__"

class BEMMemberSerializer(serializers.ModelSerializer):
    sso_account = SSOAccountSerializer()
    
    class Meta:
        model = BEMMember
        fields = ["role", "img_url"]