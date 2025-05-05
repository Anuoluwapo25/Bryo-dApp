from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentLinkViewSet, PaymentSettingsViewSet, get_auth_url, auth_callback, current_user, logout

router = DefaultRouter()
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')

urlpatterns = [
    path('api/', include(router.urls)),
    path('auth/url/', get_auth_url, name='get_auth_url'),
    path('auth/callback/', auth_callback, name='auth_callback'),
    path('user/', current_user, name='current_user'),
    path('logout/', logout, name='logout'),
]