# import requests
# import json
# import base64
# import hmac
# import hashlib
# import time
# from django.conf import settings

# class PrivyClient:
#     def __init__(self, api_key=None, api_secret=None, base_url=None):
#         self.api_key = api_key or settings.PRIVY_API_KEY
#         self.api_secret = api_secret or settings.PRIVY_API_SECRET
#         self.base_url = base_url or settings.PRIVY_BASE_URL
        
#     def _generate_headers(self):
#         """Generate headers with authentication for Privy API requests"""
#         timestamp = str(int(time.time()))
#         message = f"{timestamp}:{self.api_key}"
#         signature = hmac.new(
#             self.api_secret.encode('utf-8'),
#             message.encode('utf-8'),
#             hashlib.sha256
#         ).hexdigest()
        
#         return {
#             'Content-Type': 'application/json',
#             'X-Privy-API-Key': self.api_key,
#             'X-Privy-API-Timestamp': timestamp,
#             'X-Privy-API-Signature': signature
#         }
    
#     def create_login_link(self, email=None, redirect_url=None, **kwargs):
#         """
#         Create a login link for a user
        
#         Args:
#             email (str, optional): User's email address
#             redirect_url (str, optional): URL to redirect after authentication
#             **kwargs: Additional parameters for the login link
            
#         Returns:
#             dict: Response containing the login URL
#         """
#         endpoint = f"{self.base_url}/links"
        
#         payload = {
#             'redirectUrl': redirect_url,
#             **kwargs
#         }
        
#         if email:
#             payload['email'] = email
            
#         response = requests.post(
#             endpoint,
#             headers=self._generate_headers(),
#             json=payload
#         )
        
#         if response.status_code != 200:
#             raise Exception(f"Failed to create login link: {response.text}")
            
#         return response.json()
    
#     def verify_token(self, token):
#         """
#         Verify a Privy authentication token
        
#         Args:
#             token (str): The Privy token to verify
            
#         Returns:
#             dict: Verification result with user information
#         """
#         endpoint = f"{self.base_url}/auth/token"
        
#         payload = {
#             'token': token
#         }
        
#         response = requests.post(
#             endpoint,
#             headers=self._generate_headers(),
#             json=payload
#         )
        
#         if response.status_code != 200:
#             raise Exception(f"Failed to verify token: {response.text}")
            
#         return response.json()
    
#     def get_user(self, user_id):
#         """
#         Get user information from Privy
        
#         Args:
#             user_id (str): The Privy user ID
            
#         Returns:
#             dict: User data from Privy
#         """
#         endpoint = f"{self.base_url}/users/{user_id}"
        
#         response = requests.get(
#             endpoint,
#             headers=self._generate_headers()
#         )
        
#         if response.status_code != 200:
#             raise Exception(f"Failed to get user data: {response.text}")
            
#         return response.json()

# # Create a global instance for easy import
# privy_client = PrivyClient()