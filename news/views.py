from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import NewsArticle, Comment, Like
from .serializers import NewsArticleSerializer, CommentSerializer, LikeSerializer
from django.utils.text import slugify

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.author or request.user == obj.user or request.user.role == 'admin'

class NewsArticleViewSet(viewsets.ModelViewSet):
    queryset = NewsArticle.objects.all().order_by('-created_at')
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            slug=slugify(self.request.data.get('title'))
        )

    def perform_update(self, serializer):
        serializer.save(slug=slugify(self.request.data.get('title')))

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        article = self.get_object()
        if Like.objects.filter(article=article, user=request.user).exists():
            return Response({'error': 'You have already liked this article'}, status=status.HTTP_400_BAD_REQUEST)
        like = Like.objects.create(article=article, user=request.user)
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        article = self.get_object()
        try:
            like = Like.objects.get(article=article, user=request.user)
            like.delete()
            return Response({'status': 'Like removed'}, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({'error': 'You have not liked this article'}, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        article_id = self.request.query_params.get('article_id')
        if article_id:
            return Comment.objects.filter(article_id=article_id).order_by('-created_at')
        return super().get_queryset()

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by('-created_at')
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        article_id = self.request.query_params.get('article_id')
        if article_id:
            return Like.objects.filter(article_id=article_id).order_by('-created_at')
        return super().get_queryset()