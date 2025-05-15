from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentLinkViewSet, PaymentSettingsViewSet,
    WaitListViewSet,
    EventViewSet,
    PrivyTokenView,
    EventTicketViewSet

)


router = DefaultRouter()
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')
router.register(r'payment-links', PaymentLinkViewSet, basename='payment-links')
router.register(r'waitlist', WaitListViewSet, basename='waitlist')
router.register(r'events', EventViewSet)
router.register(r'tickets', EventTicketViewSet, basename='ticket')



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/privy/token/',  PrivyTokenView.as_view(), name='token-access'),
    # path('tickets/<int:pk>/transfer/', 
    #      EventTicketViewSet, 
    #      name='ticket-transfer'),
]