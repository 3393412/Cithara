from django.shortcuts import render

# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ShareLink
from song_api.models import Song

@csrf_exempt
def create_share_link(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            token = data.get("token")
            song_id = data.get("song_id")


            song = Song.objects.get(id=song_id)

   
            if hasattr(song, 'share_link'):
                return JsonResponse({
                    "error": "share link already exists for this song"
                }, status=400)

            link = ShareLink.objects.create(
                song=song,
                token=token
            )

            return JsonResponse({
                "message": "created",
                "token": link.token,
                "song_title": song.title,
                "user_id": song.user.id
            })

        except Song.DoesNotExist:
            return JsonResponse({"error": "song not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "invalid method"}, status=405)

@csrf_exempt
def get_share_link(request, token):
    if request.method == "GET":
        try:
            link = ShareLink.objects.get(token=token, is_active=True)
            song = link.song

            return JsonResponse({
                "token": link.token,
                "song": {
                    "id": song.id,
                    "title": song.title,
                    "genre": song.genre,
                    "mood": song.mood,
                    "path": song.path.url if song.path else None
                },
                "user_id": song.user.id
            })

        except ShareLink.DoesNotExist:
            return JsonResponse({"error": "not found"}, status=404)

    return JsonResponse({"error": "invalid method"}, status=405)
@csrf_exempt
def delete_share_link(request, token):
    if request.method == "DELETE":
        try:
            link = ShareLink.objects.get(token=token)
            link.delete()

            return JsonResponse({"message": "deleted"})

        except ShareLink.DoesNotExist:
            return JsonResponse({"error": "not found"}, status=404)

    return JsonResponse({"error": "invalid method"}, status=405)