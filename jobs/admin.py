from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'job_type', 'location', 'deadline', 'created_at', 'application_count')
    list_filter = ('job_type', 'deadline', 'created_at', 'posted_by__role')
    search_fields = ('title', 'description', 'location', 'posted_by__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def application_count(self, obj):
        return obj.applications.count()
    application_count.short_description = 'Applications'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job__job_type')
    search_fields = ('applicant__email', 'job__title', 'cover_letter')
    date_hierarchy = 'applied_at'
    ordering = ('-applied_at',)