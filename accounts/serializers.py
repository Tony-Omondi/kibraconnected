from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User, Profile, Follow
from posts.models import Post

from django.core.mail import send_mail
from django.conf import settings
import random
import string

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'role',
            'is_email_verified',
            'verification_code',
        ]
        read_only_fields = ['id', 'is_email_verified', 'verification_code']

class SimplePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'image']

class ProfileSerializer(serializers.ModelSerializer):
    user_data = UserSerializer(source='user', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'user_data',
            'bio',
            'location',
            'profile_picture',
            'followers_count',
            'following_count',
            'posts',
        ]
        read_only_fields = ['id', 'user_data', 'followers_count', 'following_count', 'posts']

    def get_followers_count(self, obj):
        return Follow.objects.filter(followed=obj.user).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.user).count()

    def get_posts(self, obj):
        user_posts = Post.objects.filter(author=obj.user)
        return SimplePostSerializer(user_posts, many=True).data

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    follower_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='follower',
        write_only=True
    )
    followed = UserSerializer(read_only=True)
    followed_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='followed',
        write_only=True
    )

    class Meta:
        model = Follow
        fields = [
            'id',
            'follower',
            'follower_id',
            'followed',
            'followed_id',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if data['follower'] == data['followed']:
            raise serializers.ValidationError("Users cannot follow themselves.")
        return data

class CustomRegisterSerializer(RegisterSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'role')
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def save(self, request):
        user = super().save(request=request)
        user.role = 'user'
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.is_active = True
        user.save()

        send_mail(
            'Email Verification Code',
            f'Your verification code is: {verification_code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user
