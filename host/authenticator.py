import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from .models import User

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
            
        try:
            # Extract the token
            auth_parts = auth_header.split(' ')
            if len(auth_parts) != 2 or auth_parts[0].lower() != 'bearer':
                return None
                
            token = auth_parts[1]
            
            # Decode the token
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Get user from token payload
            user_id = payload.get('user_id')
            if not user_id:
                raise exceptions.AuthenticationFailed('Invalid token payload')
                
            user = User.objects.get(id=user_id)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

def generate_jwt_token(user):
    """
    Generate a JWT token for the given user
    
    Args:
        user: User instance
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': str(user.id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXPIRATION_DELTA),
        'iat': datetime.datetime.utcnow(),
    }
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )