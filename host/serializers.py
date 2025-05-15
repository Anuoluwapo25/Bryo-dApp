from rest_framework import serializers
from django.utils import timezone
from .models import PaymentSettings, WaitList, Event, EventTicket, PrivyUser

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


class WaitListSerializer(serializers.Serializer):
    """Serializer for Wait Links"""
    email=serializers.CharField(required=True)

class WaitListSerializer(serializers.ModelSerializer):
    """Serializer for Wait List"""
    class Meta:
        model = WaitList
        fields = ['email']
        extra_kwargs = {
            'email': {'required': True}
        }


class PrivyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivyUser
        fields = ['privy_id', 'email', 'wallet_address', 'created_at']
        read_only_fields = ['privy_id', 'created_at']



class EventSerializer(serializers.ModelSerializer):
    # is_transferable = serializers.BooleanField(source='transferable')
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'day', 'time_from', 'time_to', 
            'location', 'virtual_link', 'description', 
            'ticket_price', 'transferable', 'capacity', 
            'visibility', 'timezone', 'event_image'
        ]
        extra_kwargs = {
            'ticket_price': {'required': False},
            'transferable': {'required': False},
            'capacity': {'required': False},
            'virtual_link': {'required': False},
            'description': {'required': False},
            'event_image': {'required': False},
        }
    
    def validate(self, data):
        if data.get('time_from') and data.get('time_to'):
            if data['time_from'] >= data['time_to']:
                raise serializers.ValidationError("End time must be after start time.")
        
        if data.get('date'):
            if data['date'] < timezone.now().date():
                raise serializers.ValidationError("Event date cannot be in the past.")
        
        return data
    



class TicketTransferSerializer(serializers.Serializer):
    new_owner_privy_id = serializers.CharField(max_length=255)
    
    def validate_new_owner_privy_id(self, value):
        try:
            PrivyUser.objects.get(privy_id=value)
        except PrivyUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value


class EventTicketSerializer(serializers.ModelSerializer):
    original_owner = PrivyUserSerializer(read_only=True)
    current_owner = PrivyUserSerializer(read_only=True)
    
    class Meta:
        model = EventTicket
        fields = '__all__'
        read_only_fields = ('created_at', 'last_transferred_at')

class TransferTicketSerializer(serializers.Serializer):
    new_owner_privy_id = serializers.CharField(required=True)

    
# class EventTicketSerializer(serializers.ModelSerializer):
#     original_owner = serializers.SlugRelatedField(
#         slug_field='privy_id',
#         queryset=PrivyUser.objects.all()
#     )
#     current_owner = serializers.SlugRelatedField(
#         slug_field='privy_id',
#         queryset=PrivyUser.objects.all()
#     )
    
#     class Meta:
#         model = EventTicket
#         fields = '__all__'
#         read_only_fields = ('created_at', 'last_transferred_at')