import json
import re
import requests
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from users.models import User
from .models import Song, GenerationJob
from .generation.service import GenerationService

def _safe_filename(name: str, fmt: str) -> str:
    """Make a safe filename from title + extension."""
    base = re.sub('[^\\w\\-. ]', '_', name or 'song').strip() or 'song'
    ext = (fmt or 'mp3').lower()
    if ext not in ('mp3', 'm4a', 'wav', 'ogg'):
        ext = 'mp3'
    return f'{base}.{ext}'

def stream_audio_proxy(audio_url: str, filename: str) -> StreamingHttpResponse:
    """Proxy-stream an external audio URL with Content-Disposition: attachment.

    Bypasses CORS (browser hits same-origin) and lets the server serve
    download semantics regardless of the upstream's headers.
    """
    try:
        upstream = requests.get(audio_url, stream=True, timeout=30)
        upstream.raise_for_status()
    except Exception as exc:
        return JsonResponse({'error': f'audio fetch failed: {exc}'}, status=502)
    content_type = upstream.headers.get('Content-Type', 'audio/mpeg')
    response = StreamingHttpResponse(upstream.iter_content(chunk_size=8192), content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    length = upstream.headers.get('Content-Length')
    if length:
        response['Content-Length'] = length
    return response

@csrf_exempt
def songs_api(request):
    if request.method == 'GET':
        song_id = request.GET.get('id')
        username = request.GET.get('username')
        if song_id:
            try:
                song = Song.objects.get(id=song_id)
                data = {'id': song.id, 'title': song.title, 'genre': song.genre, 'duration': song.duration, 'occasion': song.occasion, 'prompt': song.prompt, 'story': song.story, 'vocal': song.vocal, 'mood': song.mood, 'path': song.path.url if song.path else '', 'audio_url': song.audio_url, 'create_at': song.create_at.isoformat(), 'user': song.user.username}
                return JsonResponse(data)
            except Song.DoesNotExist:
                return JsonResponse({'error': 'Song not found'}, status=404)
        elif username:
            songs = Song.objects.filter(user__username=username)
        else:
            songs = Song.objects.all()
        data = [{'id': s.id, 'title': s.title, 'genre': s.genre, 'duration': s.duration, 'occasion': s.occasion, 'prompt': s.prompt, 'story': s.story, 'vocal': s.vocal, 'mood': s.mood, 'path': s.path.url if s.path else '', 'audio_url': s.audio_url, 'create_at': s.create_at.isoformat(), 'user': s.user.username} for s in songs]
        return JsonResponse(data, safe=False)
    elif request.method == 'POST':
        data = request.POST
        username = data.get('username')
        if not username:
            return JsonResponse({'error': 'username is required'}, status=400)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        file = request.FILES.get('path')
        song = Song.objects.create(user=user, title=data.get('title', ''), genre=data.get('genre', ''), duration=data.get('duration', 0), occasion=data.get('occasion', ''), prompt=data.get('prompt', ''), story=data.get('story', ''), vocal=data.get('vocal', ''), mood=data.get('mood', ''), path=file)
        return JsonResponse({'id': song.id, 'title': song.title, 'path': song.path.url if song.path else ''}, status=201)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            song_id = data.get('id')
            if not song_id:
                return JsonResponse({'error': 'id is required for update'}, status=400)
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return JsonResponse({'error': 'Song not found'}, status=404)
            for field in ['title', 'genre', 'duration', 'occasion', 'prompt', 'story', 'vocal', 'mood', 'path']:
                if field in data:
                    setattr(song, field, data[field])
            song.save()
            return JsonResponse({'success': True, 'id': song.id})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            song_id = data.get('id')
            if not song_id:
                return JsonResponse({'error': 'id is required for delete'}, status=400)
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return JsonResponse({'error': 'Song not found'}, status=404)
            song.delete()
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@require_http_methods(['POST'])
def generate_song(request):
    """POST /api/generate  body: JSON {prompt, title, genre, mood, vocal, occasion, story}"""
    username = request.session.get('username')
    if not username:
        return JsonResponse({'error': 'login required'}, status=401)
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    if not data.get('prompt'):
        return JsonResponse({'error': 'prompt is required'}, status=400)
    service = GenerationService()
    job = service.start(username=username, prompt=data['prompt'], title=data.get('title', ''), genre=data.get('genre', ''), mood=data.get('mood', ''), vocal=data.get('vocal', ''), occasion=data.get('occasion', ''), story=data.get('story', ''))
    return JsonResponse({'job_id': job.id, 'provider': job.provider, 'task_id': job.task_id, 'status': job.status, 'audio_url': job.audio_url or None}, status=202)

@require_http_methods(['GET'])
def generation_status(request, job_id: int):
    """GET /api/generate/<job_id>/status → poll provider (เฉพาะถ้ายังไม่จบ)"""
    try:
        job = GenerationJob.objects.get(pk=job_id)
    except GenerationJob.DoesNotExist:
        return JsonResponse({'error': 'job not found'}, status=404)
    job = GenerationService().poll(job)
    return JsonResponse({'job_id': job.id, 'provider': job.provider, 'task_id': job.task_id, 'status': job.status, 'audio_url': job.audio_url or None, 'error': job.error_message or None, 'song_id': job.song_id})

@require_http_methods(['GET'])
def download_song(request, song_id: int):
    """GET /api/songs/<song_id>/download/?fmt=mp3
    Proxy-streams the song's audio so the browser triggers a real download.
    """
    try:
        song = Song.objects.get(pk=song_id)
    except Song.DoesNotExist:
        return HttpResponseNotFound('song not found')
    audio_url = song.audio_url or (song.path.url if song.path else '')
    if not audio_url:
        return JsonResponse({'error': 'no audio for this song'}, status=404)
    fmt = request.GET.get('fmt', 'mp3')
    filename = _safe_filename(song.title, fmt)
    return stream_audio_proxy(audio_url, filename)
