from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Follow

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Kibra info', {'fields': ('role', 'is_email_verified')}),  # Updated to is_email_verified
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_email_verified'),  # Updated to is_email_verified
        }),
    )
    list_display = ('email', 'username', 'role', 'is_email_verified', 'is_staff')  # Updated to is_email_verified
    list_filter = ('role', 'is_email_verified', 'is_staff')  # Updated to is_email_verified
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location')
    search_fields = ('user__email', 'bio', 'location')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__email', 'followed__email')
    ordering = ('-created_at',)