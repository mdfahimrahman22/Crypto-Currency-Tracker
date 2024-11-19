from django.contrib import admin
from .models import BTCPrice, BTCTrackerConfig
from django.utils.timezone import localtime


@admin.register(BTCPrice)
class BTCPriceAdmin(admin.ModelAdmin):
    list_display = ['get_local_timestamp', 'buying_price',
                    'selling_price', 'recommendation']
    list_per_page = 20

    def get_local_timestamp(self, obj):
        return localtime(obj.timestamp).strftime('%b %d, %Y, %I:%M:%S %p')

    get_local_timestamp.short_description = 'Timestamp'


@admin.register(BTCTrackerConfig)
class TrackerConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'my_buying_price', 'profit_target',
                    'buying_target', 'send_selling_alert', 'send_buying_alert']
    list_display_links = ('id',)  # Make 'id' the clickable link
    list_editable = ['my_buying_price', 'profit_target',
                     'buying_target', 'send_selling_alert', 'send_buying_alert']
