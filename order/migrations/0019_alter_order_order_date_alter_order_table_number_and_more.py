# Generated by Django 5.0.1 on 2024-02-21 13:00

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0018_order_type_alter_order_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 13, 0, 34, 837141)),
        ),
        migrations.AlterField(
            model_name='order',
            name='table_number',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='order.table'),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='orderline_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 21, 13, 0, 34, 837357)),
        ),
    ]
