from django.conf import settings
from .base import AuthStrategy, UserInfo

class MockAuthStrategy(AuthStrategy):
    _FAKE_CODE = 'mock-code-abc123'

    def get_login_url(self, state: str) -> str:
        redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://127.0.0.1:8000/auth/callback/')
        return f'{redirect_uri}?code={self._FAKE_CODE}&state={state}'

    def handle_callback(self, code: str) -> UserInfo:
        return UserInfo(google_id='mock-122223', email='mock@test.com', name='Mock User', avatar_url='')
