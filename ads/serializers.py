from rest_framework import serializers
from .models import Ad
from accounts.models import User
from accounts.serializers import UserSerializer

class AdSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True
    )

    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'image', 'owner', 'owner_id', 'link', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']