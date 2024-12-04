from django.db.models import Min
from django.utils.timezone import now, timedelta
from decouple import config
from django.core.mail import send_mail
from fake_useragent import UserAgent
from time import sleep
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
# Import the model
from eth_tracker.models import ETHPrice, ETHBuyingRecord, ETHTrackerSettings


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


def track_eth_prices():
    while True:
        # Get the current configuration
        tracker_config = ETHTrackerSettings.objects.first()
        if not tracker_config:
            print("No Tracker Configuration found! Please add one in the admin panel.")
            sleep(60)  # Wait and retry
            continue

        btc_buying_records = ETHBuyingRecord.objects.filter(sold=False)
        if not len(btc_buying_records):
            print("No ETH buying records found! Please add one in the admin panel.")
            sleep(60)  # Wait and retry
            continue

        quote_data = request_data('https://api.shakepay.com/quote')

        if quote_data:
            try:
                for item in quote_data:
                    if item["symbol"] == "CAD_ETH":
                        current_buying_price = 1 / item['rate']
                        print(f'ETH Buying price: ${current_buying_price}')

                    if item["symbol"] == "ETH_CAD":
                        current_selling_price = item['rate']
                        print(f'ETH Selling price: ${current_selling_price}')

                recommendation = ""
                current_buying_price = round(current_buying_price, 2)
                current_selling_price = round(current_selling_price, 2)
                total_profit = 0
                total_target = 0
                total_buying_amount = 0
                for buying_record in btc_buying_records:
                    buying_amount = buying_record.buying_amount
                    buying_rate = buying_record.buying_rate
                    selling_value = (buying_amount/buying_rate) * \
                        current_selling_price
                    total_buying_amount += buying_amount

                    current_profit = selling_value-buying_amount

                    if current_profit >= buying_record.profit_target:
                        recommendation += f"Sell (+${round(current_profit,2)} of ${buying_amount}),\n"

                    total_profit += current_profit
                    total_target += buying_record.profit_target

                if total_profit >= total_target:
                    recommendation += f"Sell (+${round(total_profit,2)} of {total_buying_amount}),\n"
                else:
                    recommendation += f"Hold (${round(total_profit,2)} of {total_buying_amount}),\n"

                if tracker_config.send_selling_alert and 'Sell' in recommendation:
                    send_email_if_not_recent(
                        tracker_config, recommendation.strip('\n,'), current_buying_price, current_selling_price)

                if current_buying_price <= tracker_config.buying_target:
                    recommendation += "Buy,\n"
                    if tracker_config.send_buying_alert:
                        send_email_if_not_recent(
                            tracker_config, recommendation.strip('\n,'), current_buying_price, current_selling_price)

                all_time_min_buying_price = ETHPrice.objects.aggregate(
                    min_price=Min('buying_price')
                )['min_price'] or float('inf')  # Default to infinity if no records

                if current_buying_price <= all_time_min_buying_price:
                    recommendation += f"Buy (All-Time Low ${current_buying_price}),\n"
                    if tracker_config.send_buying_alert:
                        send_email_if_not_recent(
                            tracker_config, recommendation.strip(
                                '\n,'), current_buying_price, current_selling_price
                        )

                # Save data to the database
                ETHPrice.objects.create(
                    buying_price=current_buying_price,
                    selling_price=current_selling_price,
                    recommendation=recommendation.strip('\n,')
                )
                # Maintain the limit of 100 records
                ETHPrice.maintain_limit(tracker_config.data_limit)

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
        subject = f"ETH Recommendation: {recommendation}"
        message = (
            f"Dear User,\n\n"
            f"The system has a new recommendation for ETH:\n"
            f"Recommendation: {recommendation}\n"
            f"Current Buying Price: ${buying_price:.2f}\n"
            f"Current Selling Price: ${selling_price:.2f}\n\n"
            f"Please take the necessary action.\n\n"
            f"Best regards,\n"
            f"ETH Tracker System"
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
