from rest_framework import serializers
from .models import Job, JobApplication
from accounts.models import User
from accounts.serializers import UserSerializer

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    applicant_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='applicant', write_only=True
    )
    job_title = serializers.ReadOnlyField(source='job.title')

    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'applicant', 'applicant_id', 'job_title',
            'cover_letter', 'status', 'applied_at'
        ]
        read_only_fields = ['id', 'applied_at', 'status']

class JobSerializer(serializers.ModelSerializer):
    posted_by = UserSerializer(read_only=True)
    posted_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='posted_by', write_only=True
    )
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'location', 'job_type',
            'posted_by', 'posted_by_id', 'deadline', 'created_at',
            'application_count'
        ]
        read_only_fields = ['id', 'created_at']

    def get_application_count(self, obj):
        return obj.applications.count()