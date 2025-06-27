from rest_framework import serializers
from .models import Notification
from accounts.models import User
from accounts.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='sender', write_only=True
    )
    recipient = UserSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='recipient', write_only=True
    )
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'sender', 'sender_id', 'recipient', 'recipient_id',
            'notification_type', 'content_type_name', 'object_id',
            'message', 'is_read', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']