import requests
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import AuthenticationFailed

import jwt
from jwt import PyJWKClient
from django.conf import settings

def verify_privy_token(token):
    try:
        jwks_client = PyJWKClient("https://auth.privy.io/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        decoded = jwt.decode(
            token,
            signing_key.key,
            issuer="privy.io",
            audience=settings.PRIVY_APP_ID,
            algorithms=["ES256"],
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")

