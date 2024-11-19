from django.core.management.base import BaseCommand
from crypto_tracker.tasks import track_prices  # Import the function

class Command(BaseCommand):
    help = "Start BTC Price Tracker"

    def handle(self, *args, **kwargs):
        track_prices()