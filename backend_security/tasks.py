from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ['/admin', '/login']
MAX_REQUESTS_PER_HOUR = 100

@shared_task
def detect_suspicious_ips():
    """
    Flag IPs that exceed 100 requests/hour
    or access sensitive paths
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1️⃣ Detect IPs exceeding request threshold
    logs_last_hour = RequestLog.objects.filter(timestamp__gte=one_hour_ago)
    ip_counts = {}

    for log in logs_last_hour:
        ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

    for ip, count in ip_counts.items():
        if count > MAX_REQUESTS_PER_HOUR:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                reason=f"Exceeded {MAX_REQUESTS_PER_HOUR} requests/hour"
            )

    # 2️⃣ Detect IPs accessing sensitive paths
    sensitive_logs = logs_last_hour.filter(path__in=SENSITIVE_PATHS)
    for log in sensitive_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            reason=f"Accessed sensitive path: {log.path}"
        )

