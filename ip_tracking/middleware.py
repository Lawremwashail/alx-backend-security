from django.http import HttpResponseForbidden
from django.utils import timezone
from django.core.cache import cache
from ipgeolocation import IPGeolocationAPI
from .models import RequestLog, BlockedIP

GEO_CACHE_TIMEOUT = 60 * 60 * 24


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo = IPGeolocationAPI()

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
        
        # Geolocation with cache

        geo_data = cache.get(ip)
        if not geo_data:
            geo_data = self.geo.get_geolocation(ip)
            cache.set(ip, geo_data, GEO_CACHE_TIMEOUT)

        country = geo_data.get('country_name') if geo_data else None
        city = geo_data.get('city') if geo_data else None

        # Save request log
        RequestLog.objects.create(
                ip_address = ip,
                timestamp=timezone.now(),
                path=request.path
                country=country
                city=city
            
        )

        return self.get_response(request)

