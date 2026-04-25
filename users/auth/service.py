import secrets
from ..models import User
from .factory import get_auth_strategy

class AuthService:

    def __init__(self, strategy=None):
        self.strategy = strategy or get_auth_strategy()

    def get_login_url(self, request) -> str:
        state = secrets.token_urlsafe(16)
        request.session['oauth_state'] = state
        return self.strategy.get_login_url(state)

    def handle_callback(self, request, code: str, state: str) -> User:
        expected = request.session.get('oauth_state')
        if not expected or expected != state:
            raise ValueError('Invalid OAuth state — possible CSRF attempt')
        info = self.strategy.handle_callback(code)
        user, created = User.objects.get_or_create(google_id=info.google_id, defaults={'username': self._unique_username(info), 'email': info.email})
        if not created and user.email != info.email:
            user.email = info.email
            user.save(update_fields=['email'])
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        return user

    @staticmethod
    def _unique_username(info) -> str:
        base = info.email.split('@')[0] or info.google_id
        username, counter = (base, 1)
        while User.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1
        return username
