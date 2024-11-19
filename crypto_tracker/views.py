from django.shortcuts import render
from .models import BTCPrice


def main_view(request):
    # Fetch the latest BTCPrice record
    latest_price = BTCPrice.objects.order_by('-timestamp').first()

    # Prepare data for the response
    context = {
        'buying_price': latest_price.buying_price if latest_price else 'N/A',
        'selling_price': latest_price.selling_price if latest_price else 'N/A',
        'recommendation': latest_price.recommendation if latest_price else 'No Data Available',
        'timestamp': latest_price.timestamp if latest_price else 'N/A',
    }

    return render(request, 'main.html', context)
