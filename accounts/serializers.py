from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User, Profile, Follow
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

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'location', 'profile_picture']
        read_only_fields = ['id', 'user']

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
        user.role = 'user'  # Set default role
        verification_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = verification_code
        user.is_active = True  # Set active upon creation as requested
        user.save()

        # Send verification code via email
        send_mail(
            'Email Verification Code',
            f'Your verification code is: {verification_code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user