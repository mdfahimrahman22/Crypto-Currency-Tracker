from django.contrib import admin
from .models import BTCPrice, BTCTrackerConfig
from django.utils.timezone import localtime
from django.db.models import Min, Max


@admin.register(BTCPrice)
class BTCPriceAdmin(admin.ModelAdmin):
    list_display = ['get_local_timestamp', 'buying_price', 'selling_price',
                    'min_buying_price', 'max_selling_price', 'recommendation']
    list_per_page = 20

    def get_local_timestamp(self, obj):
        return localtime(obj.timestamp).strftime('%b %d, %Y, %I:%M:%S %p')

    get_local_timestamp.short_description = 'Timestamp'

    # Method to show minimum buying price
    def min_buying_price(self, obj):
        min_price = BTCPrice.objects.aggregate(
            min_price=Min('buying_price'))['min_price']
        return round(min_price, 2) if min_price is not None else 'N/A'

    min_buying_price.short_description = 'Min Buying Price'

    # Method to show maximum selling price
    def max_selling_price(self, obj):
        max_price = BTCPrice.objects.aggregate(
            max_price=Max('selling_price'))['max_price']
        return round(max_price, 2) if max_price is not None else 'N/A'

    max_selling_price.short_description = 'Max Selling Price'


@admin.register(BTCTrackerConfig)
class TrackerConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'my_buying_rate', 'my_buying_amount', 'profit_target',
                    'buying_target', 'send_selling_alert', 'send_buying_alert']
    list_display_links = ('id',)  # Make 'id' the clickable link
    list_editable = ['my_buying_amount', 'my_buying_rate', 'profit_target',
                     'buying_target', 'send_selling_alert', 'send_buying_alert']
