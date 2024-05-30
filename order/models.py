from django.db import models
from user.models import *
from products.models import *
from datetime import datetime
from django.utils import timezone
import django

class Table(models.Model):
    number = models.CharField(unique=True,max_length=20)
    hourly_charge = models.IntegerField(default=0)

class Order(models.Model):
    order_date = models.DateTimeField(default=django.utils.timezone.now)
    order_amount = models.IntegerField()
    table_number = models.ForeignKey(Table,on_delete=models.SET_NULL,null=True)
    user = models.ForeignKey(BaseUser,on_delete = models.CASCADE)
    is_paid = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    order_types = (
        ('normal', 'Normal'),
        ('delivery', 'Delivery'),
    )
    type = models.CharField(choices =order_types,default='normal',max_length=20)


class OrderLine(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    user = models.ForeignKey(BaseUser,on_delete = models.CASCADE)
    status = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled','Cancelled')
    )
    status = models.CharField(max_length=20, choices=status)
    quantity_ordered = models.IntegerField()
    orderline_date = models.DateTimeField(default=django.utils.timezone.now)