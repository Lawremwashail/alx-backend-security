from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import RequestLog, BlockedIP

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get IP
        ip = request.META.get('HTTP_X_FORWADED_FOR')
        if ip:
            ip = ip.split(',')[0]

        else:
            ip = request.META.get('REMOTE_ADDR')

        # Block if IP in blacklist

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Access Denied")


        RequestLog.objects.create(
                ip_address = ip,
                timestamp=timezone.now(),
                path=request.path
            
        )

        return self.get_response(request)

