from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProfileViewSet, FollowViewSet, verify_email
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

# Custom Google Login View
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'follows', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('social/google/', GoogleLogin.as_view(), name='google_login'),
    path('verify-email/', verify_email, name='verify_email'),
]
