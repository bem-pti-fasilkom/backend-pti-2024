from .models import BEMMember, Event
from rest_framework import serializers
from jwt.lib import SSOAccount

class BEMMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BEMMember
        fields = ["role", "img_url"]

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["start", "end"]
        
class SSOAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOAccount
        fields = ["username", "npm"]