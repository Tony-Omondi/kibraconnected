from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Job, JobApplication
from .serializers import JobSerializer, JobApplicationSerializer

class IsAdminOrEmployerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.role in ['admin', 'employer'] or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.role in ['admin', 'employer'] or request.user.is_staff)

class IsApplicantOrEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.applicant or request.user == obj.job.posted_by or request.user.role == 'admin'
        return request.user == obj.applicant

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [IsAdminOrEmployerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class JobApplicationViewSet(viewsets.ModelViewSet):
    queryset = JobApplication.objects.all().order_by('-applied_at')
    serializer_class = JobApplicationSerializer
    permission_classes = [IsApplicantOrEmployer]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'employer'] or user.is_staff:
            return JobApplication.objects.all()
        return JobApplication.objects.filter(applicant=user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request, pk=None):
        job = Job.objects.get(pk=pk)
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response({'error': 'You have already applied to this job'}, status=status.HTTP_400_BAD_REQUEST)
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=request.data.get('cover_letter', '')
        )
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)