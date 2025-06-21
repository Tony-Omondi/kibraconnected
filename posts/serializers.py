from django.conf import settings
from rest_framework import serializers
from .models import Post, Comment, Like
from accounts.serializers import UserSerializer
from accounts.models import User  # Import the User model


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'user_id']
        read_only_fields = ['id']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_id', 'content', 'image', 'created_at', 'comments', 'likes_count']
        read_only_fields = ['id', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()