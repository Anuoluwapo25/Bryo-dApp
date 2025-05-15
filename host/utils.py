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

# PRIVY_API_BASE = "https://auth.privy.io/api/v1"

# if not all([settings.PRIVY_APP_ID, settings.PRIVY_APP_SECRET, settings.FRONTEND_URL]):
#     raise ImproperlyConfigured("Missing required Privy configuration in settings.py")

# def get_privy_auth_url(state=None):
#     """Generate Privy authorization URL"""
#     params = {
#         "client_id": settings.PRIVY_APP_ID,
#         "redirect_uri": f"{settings.FRONTEND_URL}/auth/callback",
#         "response_type": "code",
#         "scope": "email wallet"
#     }
#     if state:
#         params["state"] = state
#     return f"{PRIVY_API_BASE}/authorize?" + "&".join(f"{k}={v}" for k, v in params.items())

# def exchange_code_for_token(code):
#     """Exchange authorization code for access token"""
#     response = requests.post(
#         f"{PRIVY_API_BASE}/token",
#         data={
#             "client_id": settings.PRIVY_APP_ID,
#             "client_secret": settings.PRIVY_APP_SECRET,
#             "code": code,
#             "grant_type": "authorization_code",
#             "redirect_uri": f"{settings.FRONTEND_URL}/auth/callback"
#         },
#         timeout=10
#     )
#     response.raise_for_status()
#     return response.json()

# def get_user_info(access_token):
#     """Fetch user info using access token"""
#     response = requests.get(
#         f"{PRIVY_API_BASE}/userinfo",
#         headers={"Authorization": f"Bearer {access_token}"},
#         timeout=10
#     )
#     response.raise_for_status()
#     return response.json()

# def verify_token(token):
#     """Verify the validity of an access token"""
#     try:
#         response = requests.post(
#             f"{PRIVY_API_BASE}/introspect",
#             data={
#                 "token": token,
#                 "client_id": settings.PRIVY_APP_ID,
#                 "client_secret": settings.PRIVY_APP_SECRET
#             },
#             timeout=5
#         )
#         response.raise_for_status()
#         token_data = response.json()
        
#         if not token_data.get("active"):
#             raise ValueError("Token is invalid or expired")
#         return token_data
#     except requests.exceptions.RequestException as e:
#         raise ValueError(f"Token verification failed: {str(e)}")