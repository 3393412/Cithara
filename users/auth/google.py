import urllib.parse
import requests
from django.conf import settings
from .base import AuthStrategy, UserInfo

class GoogleOAuthStrategy(AuthStrategy):
    _AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    _TOKEN_URL = 'https://oauth2.googleapis.com/token'
    _USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

    def get_login_url(self, state: str) -> str:
        params = {'client_id': settings.GOOGLE_CLIENT_ID, 'redirect_uri': settings.GOOGLE_REDIRECT_URI, 'response_type': 'code', 'scope': 'openid email profile', 'state': state}
        return f'{self._AUTH_URL}?{urllib.parse.urlencode(params)}'

    def handle_callback(self, code: str) -> UserInfo:
        token_resp = requests.post(self._TOKEN_URL, data={'code': code, 'client_id': settings.GOOGLE_CLIENT_ID, 'client_secret': settings.GOOGLE_CLIENT_SECRET, 'redirect_uri': settings.GOOGLE_REDIRECT_URI, 'grant_type': 'authorization_code'}, timeout=10)
        token_resp.raise_for_status()
        access_token = token_resp.json()['access_token']
        info_resp = requests.get(self._USERINFO_URL, headers={'Authorization': f'Bearer {access_token}'}, timeout=10)
        info_resp.raise_for_status()
        data = info_resp.json()
        return UserInfo(google_id=data['id'], email=data.get('email', ''), name=data.get('name', ''), avatar_url=data.get('picture', ''))
