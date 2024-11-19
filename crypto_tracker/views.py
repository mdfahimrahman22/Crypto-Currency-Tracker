from django.shortcuts import render
from .models import BTCPrice
import matplotlib.pyplot as plt
import io
import base64
import json

def main_view(request):
    # Fetch the latest BTCPrice record
    latest_price = BTCPrice.objects.order_by('-timestamp').first()
    
    prices = BTCPrice.objects.order_by('-timestamp')[:100][::-1]  # Reverse for chronological order

    timestamps = [price.timestamp.strftime('%b %d, %I:%M:%S %p') for price in prices]
    selling_prices = [price.selling_price for price in prices]
    buying_prices = [price.buying_price for price in prices]
    

    # Prepare data for the response
    context = {
        'buying_price': latest_price.buying_price if latest_price else 'N/A',
        'selling_price': latest_price.selling_price if latest_price else 'N/A',
        'recommendation': latest_price.recommendation if latest_price else 'No Data Available',
        'timestamp': latest_price.timestamp if latest_price else 'N/A',
        'timestamps': json.dumps(timestamps),
        'selling_prices': json.dumps(selling_prices),
        'buying_prices': json.dumps(buying_prices),
    }

    return render(request, 'main.html', context)
