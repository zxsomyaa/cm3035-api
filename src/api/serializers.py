from rest_framework import serializers
from .models import DeathRate

class DeathRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeathRate
        fields = "__all__"