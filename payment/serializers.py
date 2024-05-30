from rest_framework.serializers import ModelSerializer
from .models import *
from order.serializers import FetcbOrderSerailizer


class PayemntSerializerToAdd(ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id","customer_name","customer_phone","date_time","order","total_amount",'added_by']
class PaymentSerializer(ModelSerializer):
    order = FetcbOrderSerailizer()
    class Meta:
        model = Payment
        fields = ["id","customer_name","customer_phone","date_time","order","total_amount"]

class AllPaymentSerializer(ModelSerializer):
    order = FetcbOrderSerailizer()
    class Meta:
        model = Payment
        fields = "__all__"