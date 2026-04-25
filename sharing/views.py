import json
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import ShareLink
from song_api.models import Song
from users.models import User
from song_api.views import stream_audio_proxy, _safe_filename

@csrf_exempt
def create_share_link(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'invalid method'}, status=405)
    try:
        data = json.loads(request.body)
        song_id = data.get('song_id')
        username = data.get('username')
        song = Song.objects.get(id=song_id)
        user = User.objects.get(username=username)
        ShareLink.objects.filter(song=song, is_active=True).update(is_active=False)
        link = ShareLink.objects.create(song=song, shared_by=user)
        return JsonResponse({'token': link.token, 'song_title': song.title, 'shared_by': user.username})
    except Song.DoesNotExist:
        return JsonResponse({'error': 'song not found'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def get_share_link(request, token):
    if request.method != 'GET':
        return JsonResponse({'error': 'invalid method'}, status=405)
    try:
        link = ShareLink.objects.select_related('song', 'shared_by').get(token=token, is_active=True)
        song = link.song
        return JsonResponse({'token': link.token, 'shared_by': link.shared_by.username if link.shared_by else None, 'song': {'id': song.id, 'title': song.title, 'genre': song.genre, 'mood': song.mood, 'vocal': song.vocal, 'audio_url': song.audio_url or (song.path.url if song.path else None)}})
    except ShareLink.DoesNotExist:
        return JsonResponse({'error': 'link not found or inactive'}, status=404)

@csrf_exempt
def deactivate_share_link(request, token):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'invalid method'}, status=405)
    try:
        link = ShareLink.objects.get(token=token)
        link.is_active = False
        link.save()
        return JsonResponse({'message': 'deactivated'})
    except ShareLink.DoesNotExist:
        return JsonResponse({'error': 'not found'}, status=404)

@require_http_methods(['GET'])
def download_shared_song(request, token):
    """GET /api/share/<token>/download/?fmt=mp3
    Public — no auth required (anyone with the link can download).
    """
    try:
        link = ShareLink.objects.select_related('song').get(token=token, is_active=True)
    except ShareLink.DoesNotExist:
        return HttpResponseNotFound('share link not found or inactive')
    song = link.song
    if not song:
        return HttpResponseNotFound('song not found')
    audio_url = song.audio_url or (song.path.url if song.path else '')
    if not audio_url:
        return JsonResponse({'error': 'no audio for this song'}, status=404)
    fmt = request.GET.get('fmt', 'mp3')
    filename = _safe_filename(song.title, fmt)
    return stream_audio_proxy(audio_url, filename)
