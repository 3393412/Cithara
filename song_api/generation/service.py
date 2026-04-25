
from users.models import User
from ..models import GenerationJob, Song
from .base import GenerationRequest, GenerationResult
from .factory import get_strategy

class GenerationService:

    def __init__(self, strategy=None):
        self.strategy = strategy or get_strategy()

    def start(self, *, username: str, prompt: str, title: str='', genre: str='', mood: str='', vocal: str='', occasion: str='', story: str='') -> GenerationJob:

        user = User.objects.filter(username=username).first()
        req = GenerationRequest(prompt=prompt, title=title, genre=genre, mood=mood, vocal=vocal, occasion=occasion, story=story, style=f'{genre} {mood}'.strip(), custom_mode=bool(title))
        result: GenerationResult = self.strategy.generate(req)
        job = GenerationJob.objects.create(user=user, provider=result.provider, task_id=result.task_id, status=result.status, prompt=prompt, title=title, genre=genre, mood=mood, vocal=vocal, occasion=occasion, story=story, audio_url=result.audio_url or '', error_message=result.error or '', raw_response=result.raw)
        if result.status == 'SUCCESS' and result.audio_url and user:
            song = Song.objects.create(user=user, title=title, genre=genre, mood=mood, vocal=vocal, occasion=occasion, prompt=prompt, story=story, audio_url=result.audio_url, duration=0)
            job.song = song
            job.save(update_fields=['song'])
        return job

    def poll(self, job: GenerationJob) -> GenerationJob:
        if job.status in (GenerationJob.STATUS_SUCCESS, GenerationJob.STATUS_FAILED):
            return job
        strategy = get_strategy(job.provider)
        result = strategy.get_status(job.task_id)
        job.status = result.status
        if result.audio_url:
            job.audio_url = result.audio_url
        if result.error:
            job.error_message = result.error
        if result.raw is not None:
            job.raw_response = result.raw
        if job.status == GenerationJob.STATUS_SUCCESS and job.audio_url and (not job.song_id):
            user = job.user
            if user:
                song = Song.objects.create(user=user, title=job.title, genre=job.genre, mood=job.mood, vocal=job.vocal, occasion=job.occasion, prompt=job.prompt, story=job.story, audio_url=job.audio_url, duration=0)
                job.song = song
        job.save()
        return job
