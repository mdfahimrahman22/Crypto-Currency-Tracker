from django.core.management.base import BaseCommand
from btc_tracker.tasks import track_btc_prices 

class Command(BaseCommand):
    help = "Start BTC Price Tracker"

    def handle(self, *args, **kwargs):
        track_btc_prices()