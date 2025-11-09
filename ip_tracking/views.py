from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit


def rate_key(request):
    """
    Return the key for rate limiting:
    - Authenticated users: IP address
    - Anonymous users: IP address
    """
    return request.META.get('REMOTE_ADDR')


@csrf_exempt
@ratelimit(key=rate_key, rate='10/m', method='POST', block=False)
def login_view(request):
    """
    Login view with rate limiting.
    - Authenticated users: 10 requests/min
    - Anonymous users: 5 requests/min
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    # Determine limit based on authentication
    if request.user.is_authenticated:
        max_requests = 10
    else:
        max_requests = 5

    # Check rate limit
    if getattr(request, 'limited', False):
        return JsonResponse({'error': 'Rate limit exceeded'}, status=429)

    # Parse username/password from POST
    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'status': 'success', 'message': 'Logged in successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)

