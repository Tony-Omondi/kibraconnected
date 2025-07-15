# accounts/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'profiles', views.ProfileViewSet, basename='profiles')
router.register(r'follows', views.FollowViewSet, basename='follows')

urlpatterns = [
    path('', include(router.urls)),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
