from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import PaymentSettings
from .serializers import PaymentLinkCreateSerializer, PaymentSettingsSerializer, WaitListSerializer
from django.http import JsonResponse
from django.http import JsonResponse
from django.contrib.auth import login
from .models import PrivyUser, WaitList
from .utils import get_privy_auth_url, exchange_code_for_token, get_user_info, verify_token
import uuid
import requests
import os

class PaymentLinkViewSet(viewsets.ViewSet):
    """ViewSet for creating and managing payment links"""
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
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


class WaitListViewSet(viewsets.ModelViewSet):
    queryset = WaitList.objects.all()
    serializer_class = WaitListSerializer

    @action(detail=False, methods=['post'], url_path='lists')
    def wait_list(self, request):
        email=request.data.get('email')

        if WaitList.objects.filter(email=email).exists():
            return Response(
                {
                    'detail': 'Email already exists in waitlist'
                    
                }, status=400)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        serializer.save()
        return Response(serializer.data, status=201)

        

def privy_auth_start(request):
    """Step 1: Generate Privy auth URL"""
    state = str(uuid.uuid4())
    request.session['oauth_state'] = state
    return JsonResponse({
        'url': get_privy_auth_url(state),
        'state': state  
    })

def privy_auth_callback(request):
    """Step 2: Handle Privy callback"""
    
    if request.GET.get('state') != request.session.get('oauth_state'):
        return JsonResponse({'error': 'Invalid state'}, status=400)
    
    try:
        
        code = request.GET.get('code')
        tokens = exchange_code_for_token(code)
        privy_user = get_user_info(tokens['access_token'])
        
        
        user, created = PrivyUser.objects.update_or_create(
            privy_id=privy_user['sub'],
            defaults={
                'email': privy_user.get('email'),
                'wallet_address': privy_user.get('wallet_address'),
            }
        )
        
        login(request, user)
        
        response = JsonResponse({
            'user_id': user.id,
            'email': user.email,
            'access_token': tokens['access_token']  
        })
        response.set_cookie(
            'session_token',
            tokens['access_token'],
            httponly=True,
            secure=request.is_secure(),
            max_age=3600
        )
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def current_user_view(request):
    """Test endpoint: Get current user from DB"""
    token = request.COOKIES.get('session_token') or request.GET.get('token')
    if not token:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        privy_user = verify_token(token)
        user = PrivyUser.objects.get(privy_id=privy_user['sub'])
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'wallet_address': user.wallet_address
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=401)

def protected_test_view(request):
    """Test endpoint: For authenticated users only"""
    return JsonResponse({
        'message': 'You are authenticated!',
        'user': str(request.user) if request.user.is_authenticated else None
    })

def logout_view(request):
    """Clear session"""
    response = JsonResponse({'message': 'Logged out'})
    response.delete_cookie('session_token')
    return response