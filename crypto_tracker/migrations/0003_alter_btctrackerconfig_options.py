# Generated by Django 5.1.3 on 2024-11-18 23:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_tracker', '0002_btctrackerconfig_remove_btcprice_buying_target_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='btctrackerconfig',
            options={'verbose_name': 'BTC Tracker Config', 'verbose_name_plural': 'BTC Tracker Config'},
        ),
    ]
