# Generated by Django 4.2.9 on 2024-01-31 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_orderline_is_cancelled'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]
