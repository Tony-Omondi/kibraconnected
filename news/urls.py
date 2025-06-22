from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsArticleViewSet, CommentViewSet, LikeViewSet

router = DefaultRouter()
router.register(r'articles', NewsArticleViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]