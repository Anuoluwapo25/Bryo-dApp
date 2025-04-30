from rest_framework import serializers
from .models import PaymentSettings

class PaymentLinkCreateSerializer(serializers.Serializer):
    """Serializer for creating payment links"""
    amount = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    slug = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.CharField(required=False, allow_blank=True)

class PaymentSettingsSerializer(serializers.ModelSerializer):
    """Serializer for payment settings"""
    class Meta:
        model = PaymentSettings
        fields = ['success_message', 'inactive_message', 'redirect_url', 'payment_limit', 'branding_image']