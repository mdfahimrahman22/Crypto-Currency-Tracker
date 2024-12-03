from django.shortcuts import render, HttpResponse
from .models import ETHPrice, ETHTrackerSettings
import json
from time import sleep
from django.db.models import Min,Max
from django.utils.timezone import localtime

def eth_view(request):
    tracker_config = ETHTrackerSettings.objects.first()
    if not tracker_config:
        return HttpResponse(
            'No Tracker Configuration found! Please add one in the admin panel.')
    # Fetch the latest ETHPrice record
    latest_price = ETHPrice.objects.order_by('-timestamp').first()

    # Reverse for chronological order
    prices = ETHPrice.objects.order_by(
        '-timestamp')[:tracker_config.records_to_display_in_chart][::-1]
    
    timestamps = [localtime(price.timestamp).strftime(
        '%b %d, %I:%M:%S %p') for price in prices]
    selling_prices = [price.selling_price for price in prices]
    buying_prices = [price.buying_price for price in prices]

    # Calculate min buying price and max selling price
    
    min_buying_price = (
        ETHPrice.objects.order_by('-timestamp').aggregate(min_price=Min('buying_price'))['min_price']
        or float('inf')  # Default to infinity if no records
    )
    max_selling_price = (
        ETHPrice.objects.order_by('-timestamp').aggregate(max_price=Max('selling_price'))['max_price']
        or float('inf')  # Default to infinity if no records
    )

    # Prepare data for the response
    context = {
        'buying_price': latest_price.buying_price if latest_price else 'N/A',
        'selling_price': latest_price.selling_price if latest_price else 'N/A',
        'recommendation': latest_price.recommendation if latest_price else 'No Data Available',
        'timestamp': latest_price.timestamp if latest_price else 'N/A',
        'timestamps': json.dumps(timestamps),
        'selling_prices': json.dumps(selling_prices),
        'buying_prices': json.dumps(buying_prices),
        'min_buying_price': min_buying_price,
        'max_selling_price': max_selling_price,
    }

    return render(request, 'main.html', context)
