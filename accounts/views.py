from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Profile, Follow
from .serializers import UserSerializer, ProfileSerializer, FollowSerializer
import random
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny

User = get_user_model()

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.role == 'admin'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return User.objects.filter(is_email_verified=True)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Profile.objects.filter(user__is_email_verified=True)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    @action(detail=False, methods=['post'])
    def follow(self, request):
        followed_id = request.data.get('followed_id')
        if not followed_id:
            return Response({'error': 'followed_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            followed = User.objects.get(id=followed_id, is_email_verified=True)
            if Follow.objects.filter(follower=request.user, followed=followed).exists():
                return Response({'error': 'Already following this user'}, status=status.HTTP_400_BAD_REQUEST)
            follow = Follow.objects.create(follower=request.user, followed=followed)
            return Response(FollowSerializer(follow).data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        followed_id = request.data.get('followed_id')
        if not followed_id:
            return Response({'error': 'followed_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            followed = User.objects.get(id=followed_id)
            follow = Follow.objects.filter(follower=request.user, followed=followed)
            if not follow.exists():
                return Response({'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response({'status': 'Unfollowed'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        user_id = request.query_params.get('user_id', request.user.id)
        follows = Follow.objects.filter(followed_id=user_id)
        return Response(FollowSerializer(follows, many=True).data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        user_id = request.query_params.get('user_id', request.user.id)
        follows = Follow.objects.filter(follower_id=user_id)
        return Response(FollowSerializer(follows, many=True).data)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    code = request.data.get('verification_code')
    if not code:
        return Response(
            {'error': 'Verification code is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(verification_code=code)  # ✅ fixed line
        user.is_email_verified = True
        user.verification_code = None
        user.save()
        return Response({'detail': 'Email verified successfully.'})
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid verification code.'},
            status=status.HTTP_400_BAD_REQUEST
        )


def account_inactive(request):
    return JsonResponse({"detail": "Your account is inactive. Please verify your email."}, status=403)
