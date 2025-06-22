from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Campaign, CampaignComment, CampaignSupport
from .serializers import CampaignSerializer, CampaignCommentSerializer, CampaignSupportSerializer
from django.utils.text import slugify

class IsCreatorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.creator or request.user == obj.user or request.user.role == 'admin'

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by('-created_at')
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(
            creator=self.request.user,
            slug=slugify(self.request.data.get('title'))
        )

    def perform_update(self, serializer):
        serializer.save(slug=slugify(self.request.data.get('title')))

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def support(self, request, pk=None):
        campaign = self.get_object()
        if CampaignSupport.objects.filter(campaign=campaign, user=request.user).exists():
            return Response({'error': 'You have already supported this campaign'}, status=status.HTTP_400_BAD_REQUEST)
        support = CampaignSupport.objects.create(campaign=campaign, user=request.user)
        return Response(CampaignSupportSerializer(support).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unsupport(self, request, pk=None):
        campaign = self.get_object()
        try:
            support = CampaignSupport.objects.get(campaign=campaign, user=request.user)
            support.delete()
            return Response({'status': 'Support removed'}, status=status.HTTP_200_OK)
        except CampaignSupport.DoesNotExist:
            return Response({'error': 'You have not supported this campaign'}, status=status.HTTP_400_BAD_REQUEST)

class CampaignCommentViewSet(viewsets.ModelViewSet):
    queryset = CampaignComment.objects.all().order_by('-created_at')
    serializer_class = CampaignCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            return CampaignComment.objects.filter(campaign_id=campaign_id).order_by('-created_at')
        return super().get_queryset()

class CampaignSupportViewSet(viewsets.ModelViewSet):
    queryset = CampaignSupport.objects.all().order_by('-created_at')
    serializer_class = CampaignSupportSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            return CampaignSupport.objects.filter(campaign_id=campaign_id).order_by('-created_at')
        return super().get_queryset()