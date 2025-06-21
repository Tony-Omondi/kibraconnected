from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('role', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_verified', 'is_staff', 'is_superuser'),
        }),
    )
    ordering = ('email',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'bio')
    search_fields = ('user__email', 'location')
    list_filter = ('location',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)