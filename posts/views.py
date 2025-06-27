from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer

# 🔐 Custom permission: Only the owner can update/delete; everyone can read
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        # Otherwise, only the owner (author/user) can modify
        return obj.author == request.user if hasattr(obj, 'author') else obj.user == request.user

# ✅ Public can read posts; only logged-in users can create/update/delete their own
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

# ✅ Comments require login to view, create, update or delete
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

# ✅ Likes require login for all actions
class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ✅ Toggle like/unlike
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle(self, request, pk=None):
        post = self.get_object().post
        like = Like.objects.filter(post=post, user=request.user).first()
        if like:
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        Like.objects.create(post=post, user=request.user)
        return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)
