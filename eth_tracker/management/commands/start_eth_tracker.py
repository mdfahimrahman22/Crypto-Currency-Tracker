from django.core.management.base import BaseCommand
from eth_tracker.tasks import track_eth_prices
class Command(BaseCommand):
    help = "Start ETH Price Tracker"

    def handle(self, *args, **kwargs):
        track_eth_prices()