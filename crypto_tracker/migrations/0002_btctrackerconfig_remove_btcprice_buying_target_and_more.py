# Generated by Django 5.1.3 on 2024-11-18 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_tracker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BTCTrackerConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('my_buying_price', models.FloatField(default=0.0, help_text='Your BTC buying price.')),
                ('buying_target_threshold', models.FloatField(default=1250.61, help_text='The difference of selling price and your buying price')),
                ('buying_target', models.FloatField(default=0.0, help_text='The target profit(in CAD) for selling BTC.')),
                ('selling_target', models.FloatField(default=0.0, help_text='The price below which to buy BTC.')),
            ],
            options={
                'verbose_name': 'Tracker Configuration',
                'verbose_name_plural': 'Tracker Configurations',
            },
        ),
        migrations.RemoveField(
            model_name='btcprice',
            name='buying_target',
        ),
        migrations.RemoveField(
            model_name='btcprice',
            name='buying_target_threshold',
        ),
        migrations.RemoveField(
            model_name='btcprice',
            name='my_buying_price',
        ),
        migrations.RemoveField(
            model_name='btcprice',
            name='selling_target',
        ),
    ]
