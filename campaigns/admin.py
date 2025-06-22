from django.contrib import admin
from .models import Campaign, CampaignComment, CampaignSupport

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at', 'updated_at', 'comment_count', 'support_count')
    list_filter = ('created_at', 'updated_at', 'creator__role')
    search_fields = ('title', 'description', 'creator__email')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'

    def support_count(self, obj):
        return obj.supports.count()
    support_count.short_description = 'Supports'

@admin.register(CampaignComment)
class CampaignCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'content', 'created_at')
    list_filter = ('created_at', 'campaign')
    search_fields = ('content', 'user__email', 'campaign__title')
    ordering = ('-created_at',)

@admin.register(CampaignSupport)
class CampaignSupportAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'created_at')
    list_filter = ('created_at', 'campaign')
    search_fields = ('user__email', 'campaign__title')
    ordering = ('-created_at',)