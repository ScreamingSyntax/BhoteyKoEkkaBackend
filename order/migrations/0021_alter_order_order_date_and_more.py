# Generated by Django 5.0.1 on 2024-02-21 16:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0020_alter_order_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 16, 9, 34, 808984)),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='orderline_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 16, 9, 34, 809200)),
        ),
    ]