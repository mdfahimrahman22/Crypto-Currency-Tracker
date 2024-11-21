from django.db.models import Min
from django.utils.timezone import now, timedelta
from decouple import config
from django.core.mail import send_mail
from fake_useragent import UserAgent
from time import sleep
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from crypto_tracker.models import BTCPrice, BTCTrackerConfig  # Import the model


def request_data(url):
    while True:
        try:
            ua = UserAgent()
            headers = {
                'User-Agent': str(ua.edge),
                'Accept': 'application/json',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
                'origin': 'https://shakepay.com',
                'referer': 'https://shakepay.com/',
                'priority': 'u=1, i'
            }

            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.get(url, headers=headers, timeout=60)
            data = response.json()
            return data
        except Exception as e:
            print('Error:', e)
            print('I am going for 1 min nap!')
            sleep(60)


def track_prices():
    while True:
        # Get the current configuration
        tracker_config = BTCTrackerConfig.objects.first()
        if not tracker_config:
            print("No Tracker Configuration found! Please add one in the admin panel.")
            sleep(60)  # Wait and retry
            continue

        my_buying_amount = tracker_config.my_buying_amount
        my_buying_rate = tracker_config.my_buying_rate
        my_btc_amount = (1/my_buying_rate)*my_buying_amount

        buying_target = tracker_config.buying_target
        all_time_min_buying_price = BTCPrice.objects.aggregate(
            min_price=Min('buying_price')
        )['min_price'] or float('inf')  # Default to infinity if no records

        quote_data = request_data('https://api.shakepay.com/quote')

        if quote_data:
            try:
                for item in quote_data:
                    if item["symbol"] == "CAD_BTC":
                        new_buying_price = 1 / item['rate']
                        print(f'BTC Buying price: ${new_buying_price}')

                    if item["symbol"] == "BTC_CAD":
                        new_selling_price = item['rate']
                        print(f'BTC Selling price: ${new_selling_price}')

                recommendation = None
                new_buying_price = round(new_buying_price, 2)
                new_selling_price = round(new_selling_price, 2)

                current_profit = (
                    my_btc_amount*new_selling_price)-my_buying_amount
                if current_profit >= tracker_config.profit_target:
                    recommendation = f"Sell (+${round(current_profit,2)})"
                    if tracker_config.send_selling_alert:
                        send_email_if_not_recent(
                            tracker_config, recommendation, new_buying_price, new_selling_price)
                elif new_buying_price <= buying_target:
                    recommendation = "Buy"
                    if tracker_config.send_buying_alert:
                        send_email_if_not_recent(
                            tracker_config, recommendation, new_buying_price, new_selling_price)
                elif new_buying_price <= all_time_min_buying_price:
                    recommendation = f"Buy (All-Time Low ${new_buying_price})"
                    if tracker_config.send_buying_alert:
                        send_email_if_not_recent(
                            tracker_config, recommendation, new_buying_price, new_selling_price
                        )
                else:
                    recommendation = f"Hold (${round(current_profit,2)})"

                # Save data to the database
                BTCPrice.objects.create(
                    buying_price=new_buying_price,
                    selling_price=new_selling_price,
                    recommendation=recommendation
                )
                # Maintain the limit of 100 records
                BTCPrice.maintain_limit(tracker_config.data_limit)

            except Exception as e:
                print('Error:', e)

        sleep(tracker_config.fetch_data_duration)


def send_email_if_not_recent(tracker_config, recommendation, buying_price, selling_price):
    """
    Send an email notification with the recommendation and price details.
    """
    now_time = now()

    if tracker_config.last_email_time is None or (now_time - tracker_config.last_email_time > timedelta(minutes=tracker_config.alert_delay)):
        print('Sending email...')
        # Update the last email sent time
        subject = f"BTC Recommendation: {recommendation}"
        message = (
            f"Dear User,\n\n"
            f"The system has a new recommendation for BTC:\n"
            f"Recommendation: {recommendation}\n"
            f"Buying Price: ${buying_price:.2f}\n"
            f"Selling Price: ${selling_price:.2f}\n\n"
            f"Please take the necessary action.\n\n"
            f"Best regards,\n"
            f"BTC Tracker System"
        )
        from_email = config('EMAIL_HOST_USER')
        # Replace with the recipient's email
        recipient_list = [config('EMAIL_RECIPIENT')]

        try:
            send_mail(subject, message, from_email, recipient_list)
            print(f"Email sent successfully: {subject}")
            tracker_config.last_email_time = now_time
            tracker_config.save()
        except Exception as e:
            print(f"Failed to send email: {e}")
