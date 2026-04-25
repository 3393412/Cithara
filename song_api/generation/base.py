"""Abstract strategy interface + request/result DTOs.

ใช้ dataclass เพื่อให้ view/service/strategy ส่งข้อมูลหากันโดยไม่ต้องผูกกับ Django model
(กัน strategy รู้จัก ORM ตรง ๆ → ทดสอบง่าย)
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class GenerationRequest:
    prompt: str
    title: str = ''
    genre: str = ''
    mood: str = ''
    vocal: str = ''
    occasion: str = ''
    story: str = ''
    style: str = ''
    instrumental: bool = False
    custom_mode: bool = False
    model: str = 'V3_5'

@dataclass
class GenerationResult:
    task_id: str
    status: str
    provider: str
    audio_url: Optional[str] = None
    error: Optional[str] = None
    raw: Optional[dict[str, Any]] = field(default=None, repr=False)

class SongGeneratorStrategy(ABC):
    """ทุก strategy ต้องมี 2 method นี้"""
    provider_name: str = 'base'

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        """เริ่มงาน generate ใหม่ — ต้อง return task_id + สถานะเริ่มต้น"""

    @abstractmethod
    def get_status(self, task_id: str) -> GenerationResult:
        """ดูสถานะงานเก่า — สำหรับ polling"""
