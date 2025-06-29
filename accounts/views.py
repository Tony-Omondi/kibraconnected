from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, Follow
from .serializers import UserSerializer, ProfileSerializer, FollowSerializer
from django.core.mail import send_mail
from django.conf import settings
import random
import string

User = get_user_model()

# ✅ Permission for owners or admins
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.role == 'admin'

# ✅ User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return User.objects.filter(is_email_verified=True)

# ✅ Profile ViewSet
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Profile.objects.filter(user__is_email_verified=True)

# ✅ Follow ViewSet
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

# ✅ Email verification endpoint
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
        user = User.objects.get(verification_code=code)
        user.is_email_verified = True
        user.is_active = True  # Already active on creation, but ensure consistency
        user.verification_code = None
        user.save()
        return Response({'detail': 'Email verified successfully.'})
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid verification code.'},
            status=status.HTTP_400_BAD_REQUEST
        )

# ✅ Login endpoint
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if email is None or password is None:
        return Response(
            {'error': 'Please provide both email and password.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, email=email, password=password)
    
    if not user:
        return Response(
            {'error': 'Unable to log in with provided credentials.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.is_email_verified:
        return Response(
            {'error': 'Please verify your email before logging in.'},
            status=status.HTTP_403_FORBIDDEN
        )

    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user.role,
        },
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })

# ✅ Forgot Password - Request Reset Code
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=email)
        reset_code = ''.join(random.choices(string.digits, k=6))
        user.verification_code = reset_code  # Reuse verification_code field for reset
        user.save()

        send_mail(
            'Password Reset Code',
            f'Your password reset code is: {reset_code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return Response({'detail': 'Reset code sent to your email.'})
    except User.DoesNotExist:
        return Response(
            {'error': 'No user found with this email.'},
            status=status.HTTP_404_NOT_FOUND
        )

# ✅ Reset Password
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    code = request.data.get('verification_code')
    new_password = request.data.get('new_password')

    if not email or not code or not new_password:
        return Response(
            {'error': 'Email, verification code, and new password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=email, verification_code=code)
        user.set_password(new_password)
        user.verification_code = None  # Clear the code after reset
        user.save()
        return Response({'detail': 'Password reset successfully.'})
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid email or verification code.'},
            status=status.HTTP_400_BAD_REQUEST
        )

# ✅ Inactive account message (can be removed if no longer relevant)
def account_inactive(request):
    return JsonResponse({"detail": "Your account is inactive. Please verify your email."}, status=403)