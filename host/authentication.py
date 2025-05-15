from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import PrivyUser
from .utils import verify_privy_token

class PrivyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        decoded = verify_privy_token(token)
        privy_user, _ = PrivyUser.objects.get_or_create(
            privy_id=decoded["sub"],
            defaults={
                "wallet_address": decoded.get("wallet", {}).get("address", ""),
                "email": decoded.get("email", {}).get("address", ""),
            }
        )
        return (privy_user, None) 