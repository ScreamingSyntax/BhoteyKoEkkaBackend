# Generated by Django 5.0.1 on 2024-02-10 20:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_orderline_order_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderline',
            old_name='order_date',
            new_name='orderline_date',
        ),
    ]