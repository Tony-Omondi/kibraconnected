from rest_framework import serializers
from .models import Campaign, CampaignComment, CampaignSupport
from accounts.models import User
from accounts.serializers import UserSerializer
from django.utils.text import slugify

class CampaignCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    campaign_title = serializers.ReadOnlyField(source='campaign.title')

    class Meta:
        model = CampaignComment
        fields = ['id', 'campaign', 'user', 'user_id', 'campaign_title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class CampaignSupportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    campaign_title = serializers.ReadOnlyField(source='campaign.title')

    class Meta:
        model = CampaignSupport
        fields = ['id', 'campaign', 'user', 'user_id', 'campaign_title', 'created_at']
        read_only_fields = ['id', 'created_at']

class CampaignSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    creator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='creator', write_only=True
    )
    comment_count = serializers.SerializerMethodField()
    support_count = serializers.SerializerMethodField()
    comments = CampaignCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'creator', 'creator_id', 'title', 'slug', 'description',
            'image', 'created_at', 'updated_at', 'comment_count', 'support_count', 'comments'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_support_count(self, obj):
        return obj.supports.count()

    def validate_title(self, value):
        if self.instance is None and Campaign.objects.filter(slug=slugify(value)).exists():
            raise serializers.ValidationError("A campaign with this title already exists.")
        return value