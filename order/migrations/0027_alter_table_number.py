# Generated by Django 5.0.1 on 2024-02-22 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0026_alter_order_order_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
