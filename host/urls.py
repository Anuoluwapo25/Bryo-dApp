from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentLinkViewSet, PaymentSettingsViewSet,
    WaitListViewSet,
    # EventViewSet,
    drf_protected_view,

)


router = DefaultRouter()
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')
router.register(r'waitlist', WaitListViewSet, basename='waitlist')
# router.register(r'events', EventViewSet)



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/privy/token/', drf_protected_view, name='token-access'),
]