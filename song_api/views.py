from django.shortcuts import render

# Create your views here.
# from rest_framework import viewsets
# from .serializers import SongSerializer


from django.http import JsonResponse
from .models import Song
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def songs_api(request):

    if request.method == "GET":
        song_id = request.GET.get('id')
        username = request.GET.get('username')

        if song_id:
            try:
                song = Song.objects.get(id=song_id)
                data = {
                    "id": song.id,
                    "title": song.title,
                    "genre": song.genre,
                    "duration": song.duration,
                    "occasion": song.occasion,
                    "prompt": song.prompt,
                    "story": song.story,
                    "vocal": song.vocal,
                    "mood": song.mood,
                    "path": song.path.url if song.path else "",
                    "create_at": song.create_at.isoformat(),
                    "user": song.user.username
                }
                return JsonResponse(data)
            except Song.DoesNotExist:
                return JsonResponse({"error": "Song not found"}, status=404)
        
        elif username:
            songs = Song.objects.filter(user__username=username)
        else:
            songs = Song.objects.all()
        
        data = [
            {
                "id": s.id,
                "title": s.title,
                "genre": s.genre,
                "duration": s.duration,
                "occasion": s.occasion,
                "prompt": s.prompt,
                "story": s.story,
                "vocal": s.vocal,
                "mood": s.mood,
                "path": s.path.url if s.path else "",
                "create_at": s.create_at.isoformat(),
                "user": s.user.username
            }
            for s in songs
        ]
        return JsonResponse(data, safe=False)

    elif request.method == "POST":
        data = request.POST

        username = data.get("username")
        if not username:
            return JsonResponse({"error": "username is required"}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        file = request.FILES.get("path")

        song = Song.objects.create(
            user=user,
            title=data.get("title", ""),
            genre=data.get("genre", ""),
            duration=data.get("duration", 0),
            occasion=data.get("occasion", ""),
            prompt=data.get("prompt", ""),
            story=data.get("story", ""),
            vocal=data.get("vocal", ""),
            mood=data.get("mood", ""),
            path=file,  
        )
        return JsonResponse({
            "id": song.id,
            "title": song.title,
            "path": song.path.url if song.path else "",
        }, status=201)

    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            song_id = data.get("id")
            if not song_id:
                return JsonResponse({"error": "id is required for update"}, status=400)
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return JsonResponse({"error": "Song not found"}, status=404)


            for field in ["title","genre","duration","occasion","prompt","story","vocal","mood","path"]:
                if field in data:
                    setattr(song, field, data[field])
            song.save()

            return JsonResponse({"success": True, "id": song.id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            song_id = data.get("id")
            if not song_id:
                return JsonResponse({"error": "id is required for delete"}, status=400)
            try:
                song = Song.objects.get(id=song_id)
            except Song.DoesNotExist:
                return JsonResponse({"error": "Song not found"}, status=404)

            song.delete()
            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)