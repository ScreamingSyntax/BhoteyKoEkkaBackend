# Generated by Django 5.0.1 on 2024-02-21 23:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0023_alter_order_order_date_alter_orderline_item_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 23, 24, 18, 106036)),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='orderline_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 23, 24, 18, 106264)),
        ),
    ]
