from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    help = "Add an IP address to the blacklist"

    def add_arguments(self, parse):
        parser.add_argument("ip_address", type=str, help="IP address to block")

    def handle(self, *args, **kwargs):
        ip = kwargs['ip_address']

        # create new entry if it doesn't exists

        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked IP: {ip}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP already blocked: {ip}"))
