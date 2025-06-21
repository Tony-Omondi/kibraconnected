from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User, Profile

class CustomRegisterSerializer(RegisterSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='user')

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['role'] = self.validated_data.get('role', 'user')
        return data

    def save(self, request):
        user = super().save(request)
        Profile.objects.create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_verified']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'profile_picture']