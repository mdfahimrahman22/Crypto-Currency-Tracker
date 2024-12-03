from django.contrib import admin
from .models import ETHPrice, ETHBuyingRecord, ETHTrackerSettings
from django.utils.timezone import localtime
from django.db.models import Min, Max

@admin.action(description="Mark selected records as sold")
def mark_as_sold(modeladmin, request, queryset):
    queryset.update(sold=True)

@admin.register(ETHTrackerSettings)
class ETHTrackerSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'buying_target', 'fetch_data_duration',
                    'send_selling_alert', 'send_buying_alert', 'records_to_display_in_chart']
    list_display_links = ('id',)  # Make 'id' the clickable link
    list_editable = ['buying_target', 'fetch_data_duration',
                     'send_selling_alert', 'send_buying_alert', 'records_to_display_in_chart']
    readonly_fields=['last_email_time']


@admin.register(ETHPrice)
class ETHPriceAdmin(admin.ModelAdmin):
    list_display = ['get_local_timestamp', 'buying_price', 'selling_price',
                    'min_buying_price', 'max_selling_price', 'recommendation']
    list_per_page = 20

    def get_local_timestamp(self, obj):
        return localtime(obj.timestamp).strftime('%b %d, %Y, %I:%M:%S %p')

    get_local_timestamp.short_description = 'Timestamp'

    # Method to show minimum buying price
    def min_buying_price(self, obj):
        min_price = ETHPrice.objects.aggregate(
            min_price=Min('buying_price'))['min_price']
        return round(min_price, 2) if min_price is not None else 'N/A'

    min_buying_price.short_description = 'Min Buying Price'

    # Method to show maximum selling price
    def max_selling_price(self, obj):
        max_price = ETHPrice.objects.aggregate(
            max_price=Max('selling_price'))['max_price']
        return round(max_price, 2) if max_price is not None else 'N/A'

    max_selling_price.short_description = 'Max Selling Price'


@admin.register(ETHBuyingRecord)
class ETHBuyingRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'buying_rate',
                    'buying_amount', 'profit_target', 'date', 'sold']
    list_filter = ['sold']
    list_display_links = ('id',)  # Make 'id' the clickable link
    list_editable = ['buying_rate',
                     'buying_amount', 'profit_target', 'sold']
    list_per_page = 20
    actions = [mark_as_sold]