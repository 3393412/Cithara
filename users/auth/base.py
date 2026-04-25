from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class UserInfo:
    google_id: str
    email: str
    name: str = ''
    avatar_url: str = ''

class AuthStrategy(ABC):

    @abstractmethod
    def get_login_url(self, state: str) -> str:
        ...

    @abstractmethod
    def handle_callback(self, code: str) -> UserInfo:
        ...
