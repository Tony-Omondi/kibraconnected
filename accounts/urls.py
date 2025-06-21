from django.urls import path
from .views import ProfileView, GoogleLogin

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('social/google/', GoogleLogin.as_view(), name='google_login'),
]