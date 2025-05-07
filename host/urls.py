from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentLinkViewSet, PaymentSettingsViewSet,
    WaitListViewSet,
    privy_auth_start,
    privy_auth_callback,
    current_user_view,
    protected_test_view,
    logout_view
)


router = DefaultRouter()
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')
router.register(r'waitlist', WaitListViewSet, basename='waitlist')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/start/', privy_auth_start, name='privy-auth-start'),
    path('api/auth/callback/', privy_auth_callback, name='privy-auth-callback'),
    
    path('api/current-user/', current_user_view, name='current-user'),
    path('api/protected/', protected_test_view, name='protected-test'),
    path('api/logout/', logout_view, name='logout'),
]