from rest_framework import serializers
from .models import Post, Comment, Like
from accounts.serializers import UserSerializer
from accounts.models import User

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False
    )
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'user_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False
    )

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'user_id']
        read_only_fields = ['id', 'user']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'content',
            'image',
            'created_at',
            'comments',
            'likes_count',
            'comments_count',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'comments', 'likes_count', 'comments_count']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate(self, data):
        if not data.get('content') and not data.get('image'):
            raise serializers.ValidationError("At least one of content or image must be provided.")
        return data