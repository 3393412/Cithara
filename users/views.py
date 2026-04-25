from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .auth.service import AuthService
from .models import User

def login_view(request):
    url = AuthService().get_login_url(request)
    return redirect(url)

def callback_view(request):
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')
    try:
        AuthService().handle_callback(request, code, state)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return redirect('/')

@csrf_exempt
@require_http_methods(['POST'])
def logout_view(request):
    request.session.flush()
    return JsonResponse({'success': True})

@require_http_methods(['GET'])
def me_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'not authenticated'}, status=401)
    try:
        user = User.objects.get(id=user_id)
        return JsonResponse({'username': user.username, 'email': user.email, 'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}', 'tour_seen': user.tour_seen})
    except User.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=401)

@csrf_exempt
@require_http_methods(['POST'])
def tour_complete_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'not authenticated'}, status=401)
    try:
        user = User.objects.get(id=user_id)
        user.tour_seen = True
        user.save(update_fields=['tour_seen'])
        return JsonResponse({'success': True})
    except User.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=401)
