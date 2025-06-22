from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/social/', include('allauth.socialaccount.urls')),

    # ✅ Fix the email confirmation route
    re_path(
        r'^api/auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$',
        confirm_email,
        name='account_confirm_email'
    ),

    path('api/posts/', include('posts.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/marketplace/', include('marketplace.urls')),
    path('api/campaigns/', include('campaigns.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
