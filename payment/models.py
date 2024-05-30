from django.db import models
from order.models import Order,Table
from user.models import BaseUser
from django.utils import timezone
import django

class Payment(models.Model):
    customer_name = models.CharField(max_length=100,null=True)
    customer_phone = models.CharField(null=True,max_length=100)
    date_time = models.DateTimeField(default=django.utils.timezone.now)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True)
    total_amount = models.IntegerField()
    added_by = models.ForeignKey(BaseUser,null=True,on_delete=models.CASCADE)