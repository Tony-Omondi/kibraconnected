from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet, ProfileViewSet, FollowViewSet, verify_email, login_view, forgot_password, reset_password

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'profiles', views.ProfileViewSet, basename='profiles')
router.register(r'follows', views.FollowViewSet, basename='follows')

urlpatterns = [
    path('', include(router.urls)),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),  # Removed /api/accounts/ prefix here
    path('reset-password/', views.reset_password, name='reset_password'),    # Removed /api/accounts/ prefix here
    path('', include(router.urls)),
]
