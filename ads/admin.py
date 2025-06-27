from django.contrib import admin
from .models import Ad

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'is_active', 'created_at', 'link')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'owner__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)