from django.conf import settings
from .base import AuthStrategy
from .google import GoogleOAuthStrategy
from .mock import MockAuthStrategy
_REGISTRY: dict[str, type[AuthStrategy]] = {'google': GoogleOAuthStrategy, 'mock': MockAuthStrategy}

def get_auth_strategy(name: str=None) -> AuthStrategy:
    key = (name or settings.AUTH_STRATEGY).lower()
    cls = _REGISTRY.get(key)
    if cls is None:
        raise ValueError(f'Unknown auth strategy: {key!r}. Choose from: {list(_REGISTRY)}')
    return cls()
