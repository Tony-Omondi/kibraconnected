from rest_framework import serializers
from .models import NewsArticle, Comment, Like
from accounts.models import User
from accounts.serializers import UserSerializer
from django.utils.text import slugify

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    article_title = serializers.ReadOnlyField(source='article.title')

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'user_id', 'article_title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    article_title = serializers.ReadOnlyField(source='article.title')

    class Meta:
        model = Like
        fields = ['id', 'article', 'user', 'user_id', 'article_title', 'created_at']
        read_only_fields = ['id', 'created_at']

class NewsArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='author', write_only=True
    )
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = NewsArticle
        fields = [
            'id', 'author', 'author_id', 'title', 'slug', 'content',
            'image', 'created_at', 'updated_at', 'comment_count', 'like_count', 'comments'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_like_count(self, obj):
        return obj.likes.count()

    def validate_title(self, value):
        if self.instance is None and NewsArticle.objects.filter(slug=slugify(value)).exists():
            raise serializers.ValidationError("An article with this title already exists.")
        return value