from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, ActivationView, UserViewSet, CustomTokenRefreshView
from teams.views import MembershipApplicationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/activate/', ActivationView.as_view(), name='activate'),
    
    # Membership endpoints
    path('membership/apply/', MembershipApplicationViewSet.as_view({'post': 'create'}), name='membership_apply'),
] + router.urls
