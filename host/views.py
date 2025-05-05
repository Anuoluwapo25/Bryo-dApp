from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PaymentSettings
from .serializers import PaymentLinkCreateSerializer, PaymentSettingsSerializer
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .utils import get_privy_auth_url, exchange_code_for_user
from .models import PrivyUser
import requests
import os

class PaymentLinkViewSet(viewsets.ViewSet):
    """ViewSet for creating and managing payment links"""
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_payment_link(self, request):
        """Create a new payment link"""
        serializer = PaymentLinkCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        settings = PaymentSettings.load()
        
        payload = {
            "amount": data['amount'],
            "description": data['description'],
            "name": data['name']
        }
        
        if 'slug' in data and data['slug']:
            payload["slug"] = data['slug']
        if 'metadata' in data and data['metadata']:
            payload["metadata"] = data['metadata']
        
        if settings.success_message:
            payload["successMessage"] = settings.success_message
        if settings.inactive_message:
            payload["inactiveMessage"] = settings.inactive_message
        if settings.redirect_url:
            payload["redirectUrl"] = settings.redirect_url
        if settings.payment_limit:
            payload["paymentLimit"] = str(settings.payment_limit)
        
        url = "https://api.blockradar.co/v1/payment_links"
        headers = {
            "x-api-key": os.environ.get("BLOCKRADAR_API_KEY")
        }
        
        files = {}
        if settings.branding_image:
            files = {
                "file": (
                    os.path.basename(settings.branding_image.name),
                    settings.branding_image.open(),
                    'image/jpeg'
                )
            }
        
        try:
            response = requests.post(url, data=payload, files=files or None, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            return Response({
                'success': True,
                'paymentUrl': result['data']['url'],
                'paymentId': result['data']['id'],
                'message': result['message']
            }, status=status.HTTP_201_CREATED)
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            try:
                if e.response and e.response.json():
                    error_message = e.response.json().get('message', str(e))
            except:
                pass
                
            return Response({
                'success': False,
                'error': error_message
            }, status=status.HTTP_400_BAD_REQUEST)

class PaymentSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment settings"""
    queryset = PaymentSettings.objects.all()
    serializer_class = PaymentSettingsSerializer
    
    def get_object(self):
        """Always return the singleton settings object"""
        return PaymentSettings.load()


@api_view(['GET'])
def get_auth_url(request):
    auth_url = get_privy_auth_url()
    return Response({'url': auth_url})

@api_view(['GET'])
def auth_callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Missing authorization code'}, status=400)
    
    try:
        # Get user data from Privy
        privy_user, token = exchange_code_for_user(code)
        
        # Save or update user
        user, created = PrivyUser.objects.update_or_create(
            privy_id=privy_user['id'],
            defaults={
                'email': privy_user.get('email', {}).get('address'),
                'wallet_address': privy_user.get('wallet', {}).get('address'),
            }
        )
        
        response = JsonResponse({'success': True})
        response.set_cookie(
            key='session_token',
            value=token,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite='Lax',
            max_age=604800  # 7 days
        )
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def current_user(request):
    token = request.COOKIES.get('session_token')
    if not token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        privy_user = privy_client.verify_token(token)
        user = PrivyUser.objects.get(privy_id=privy_user['id'])
        return JsonResponse({
            'email': user.email,
            'wallet_address': user.wallet_address
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=401)

@api_view(['POST'])
def logout(request):
    response = JsonResponse({'success': True})
    response.delete_cookie('session_token')
    return response