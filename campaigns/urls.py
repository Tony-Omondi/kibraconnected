from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, CampaignCommentViewSet, CampaignSupportViewSet

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)
router.register(r'comments', CampaignCommentViewSet)
router.register(r'supports', CampaignSupportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]