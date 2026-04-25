"""Centralized strategy selection — แก้ที่เดียวพอ ไม่กระจาย if/else ทั่ว codebase"""
from django.conf import settings
from .base import SongGeneratorStrategy
from .mock import MockSongGeneratorStrategy
from .suno import SunoSongGeneratorStrategy
_REGISTRY: dict[str, type[SongGeneratorStrategy]] = {'mock': MockSongGeneratorStrategy, 'suno': SunoSongGeneratorStrategy}

def get_strategy(name: str | None=None) -> SongGeneratorStrategy:
    key = (name or getattr(settings, 'GENERATOR_STRATEGY', 'mock')).lower()
    if key not in _REGISTRY:
        raise ValueError(f'Unknown generator strategy: {key!r}. Available: {list(_REGISTRY)}')
    return _REGISTRY[key]()

def register_strategy(name: str, cls: type[SongGeneratorStrategy]) -> None:
    _REGISTRY[name.lower()] = cls
