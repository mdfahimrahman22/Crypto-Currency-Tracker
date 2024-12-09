from django.db import models
from datetime import date

class BTCTrackerSettings(models.Model):
    buying_target = models.FloatField(
        default=0.0, help_text="The price below which to buy BTC.")
    fetch_data_duration = models.IntegerField(
        default=30, help_text="Sleep time after API call in second")
    send_selling_alert = models.BooleanField(default=True)
    send_buying_alert = models.BooleanField(default=True)
    alert_delay = models.IntegerField(
        default=30, help_text="The delay of sending email in minutes")
    data_limit = models.IntegerField(
        default=2880, help_text="Max records will be stored")
    records_to_display_in_chart = models.IntegerField(
        default=100, help_text="Last X records to display in chart")
    last_email_time = models.DateTimeField(
        null=True, blank=True, help_text="Last time an email was sent.")

    def __str__(self):
        return "BTC Tracker Settings"

    class Meta:
        verbose_name = "BTC Tracker Settings"
        verbose_name_plural = "BTC Tracker Settings"


class BTCBuyingRecord(models.Model):
    buying_rate = models.FloatField(
        default=1, help_text="Your BTC buying rate (1 BTC Price).")
    buying_amount = models.FloatField(
        default=0.0, help_text="Your BTC buying amount in CAD.")
    profit_target = models.FloatField(
        default=0.0, help_text="The target profit(in CAD) for selling BTC.")
    date = models.DateField(default=date.today)
    sold = models.BooleanField(default=False)

    class Meta:
        verbose_name = "BTC Buying Record"
        verbose_name_plural = "BTC Buying Records"


class BTCPrice(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    buying_price = models.FloatField()
    selling_price = models.FloatField()
    recommendation = models.TextField(null=True, blank=True)  # "Buy", "Sell", or "Hold"

    def __str__(self):
        return f"BTC Price at {self.timestamp}: Buy={self.buying_price}, Sell={self.selling_price}"

    @staticmethod
    def maintain_limit(limit=100):
        """Ensure the table only contains the last `limit` records."""
        total_records = BTCPrice.objects.count()
        if total_records > limit:
            excess_records = total_records - limit
            oldest_records = BTCPrice.objects.order_by('timestamp')[
                :excess_records]
            BTCPrice.objects.filter(
                id__in=[record.id for record in oldest_records]).delete()

    class Meta:
        verbose_name = "BTC Price"
        verbose_name_plural = "BTC Prices"
