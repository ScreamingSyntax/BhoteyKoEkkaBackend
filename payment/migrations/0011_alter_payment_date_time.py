# Generated by Django 5.0.1 on 2024-02-22 16:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_alter_payment_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]