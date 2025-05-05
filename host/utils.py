from privy_auth import PrivyClient
from django.conf import settings

privy_client = PrivyClient(
    app_id=settings.PRIVY_APP_ID,
    app_secret=settings.PRIVY_APP_SECRET
)

def get_privy_auth_url():
    return privy_client.generate_auth_url(
        redirect_url=f"{settings.FRONTEND_URL}/auth/callback"
    )

def exchange_code_for_user(code):
    return privy_client.authenticate(code)