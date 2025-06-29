from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import account_inactive, verify_email
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, ProfileViewSet, FollowViewSet

router = DefaultRouter()
router.register(r'api/accounts/users', UserViewSet, basename='users')
router.register(r'api/accounts/profiles', ProfileViewSet, basename='profiles')
router.register(r'api/accounts/follows', FollowViewSet, basename='follows')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),

    # ✅ Confirm email
    re_path(
        r'^api/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        confirm_email,
        name='account_confirm_email'
    ),

    # ✅ Add verify email endpoint
    path('api/auth/verify-email/', verify_email, name='verify_email'),

    path('api/posts/', include('posts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/marketplace/', include('marketplace.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/ads/', include('ads.urls')),
    path("account/inactive/", account_inactive, name="account_inactive"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + router.urls  # Include router URLs