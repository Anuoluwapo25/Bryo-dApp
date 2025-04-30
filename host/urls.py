from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentLinkViewSet, PaymentSettingsViewSet

router = DefaultRouter()
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')

urlpatterns = [
    path('api/', include(router.urls)),
]