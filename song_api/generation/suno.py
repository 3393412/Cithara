"""Suno API strategy — เรียก sunoapi.org ด้วย Bearer token."""
import requests
from django.conf import settings
from .base import GenerationRequest, GenerationResult, SongGeneratorStrategy

class SunoSongGeneratorStrategy(SongGeneratorStrategy):
    provider_name = 'suno'

    def __init__(self, api_key: str | None=None, base_url: str | None=None, timeout: int=30):
        self.api_key = api_key or getattr(settings, 'SUNO_API_KEY', '')
        self.base_url = (base_url or getattr(settings, 'SUNO_API_BASE_URL', 'https://api.sunoapi.org/api/v1')).rstrip('/')
        self.timeout = timeout
        if not self.api_key:
            raise ValueError('SUNO_API_KEY is not configured')

    def _headers(self) -> dict:
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    def generate(self, request: GenerationRequest) -> GenerationResult:
        payload: dict = {'prompt': request.prompt, 'customMode': request.custom_mode, 'instrumental': request.instrumental, 'model': request.model, 'callBackUrl': 'https://example.com/callback'}
        print('PAYLOAD TO SUNO:', payload)
        if request.custom_mode:
            payload['title'] = request.title or 'Untitled'
            payload['style'] = request.style or f'{request.genre} {request.mood}'.strip() or 'pop'
        try:
            resp = requests.post(f'{self.base_url}/generate', json=payload, headers=self._headers(), timeout=self.timeout)
            print('STATUS CODE:', resp.status_code)
            print('RESPONSE:', resp.json())
            data = resp.json() if resp.content else {}
        except requests.RequestException as e:
            return GenerationResult(task_id='', status='FAILED', provider=self.provider_name, error=str(e))
        if resp.status_code != 200 or data.get('code') != 200:
            return GenerationResult(task_id='', status='FAILED', provider=self.provider_name, error=data.get('msg') or f'HTTP {resp.status_code}', raw=data)
        task_id = (data.get('data') or {}).get('taskId', '')
        return GenerationResult(task_id=task_id, status='PENDING', provider=self.provider_name, raw=data)

    def get_status(self, task_id: str) -> GenerationResult:
        try:
            resp = requests.get(f'{self.base_url}/generate/record-info', params={'taskId': task_id}, headers=self._headers(), timeout=self.timeout)
            data = resp.json() if resp.content else {}
        except requests.RequestException as e:
            return GenerationResult(task_id=task_id, status='FAILED', provider=self.provider_name, error=str(e))
        if resp.status_code != 200 or data.get('code') != 200:
            return GenerationResult(task_id=task_id, status='FAILED', provider=self.provider_name, error=data.get('msg') or f'HTTP {resp.status_code}', raw=data)
        info = data.get('data') or {}
        status = info.get('status', 'PENDING')
        audio_url = None
        response_block = info.get('response') or {}
        tracks = response_block.get('sunoData') or []
        if tracks:
            first = tracks[0]
            audio_url = first.get('audioUrl') or first.get('streamAudioUrl')
        return GenerationResult(task_id=task_id, status=status, provider=self.provider_name, audio_url=audio_url, raw=data)
