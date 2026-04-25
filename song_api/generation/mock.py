"""Mock strategy — offline, deterministic, ไม่ต้องต่อเน็ต."""
import uuid
from .base import GenerationRequest, GenerationResult, SongGeneratorStrategy

class MockSongGeneratorStrategy(SongGeneratorStrategy):
    provider_name = 'mock'
    FIXED_AUDIO_URL = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3'

    def generate(self, request: GenerationRequest) -> GenerationResult:
        task_id = f'mock-{uuid.uuid4().hex[:12]}'
        return GenerationResult(task_id=task_id, status='SUCCESS', provider=self.provider_name, audio_url=self.FIXED_AUDIO_URL, raw={'mock': True, 'prompt': request.prompt, 'title': request.title})

    def get_status(self, task_id: str) -> GenerationResult:
        return GenerationResult(task_id=task_id, status='SUCCESS', provider=self.provider_name, audio_url=self.FIXED_AUDIO_URL)
