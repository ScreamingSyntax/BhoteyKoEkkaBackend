# Generated by Django 5.0.1 on 2024-02-21 12:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0017_alter_order_order_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='type',
            field=models.CharField(choices=[('normal', 'Normal'), ('delivery', 'Delivery')], default='normal', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 12, 54, 35, 257303)),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='orderline_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 12, 54, 35, 257576)),
        ),
    ]
