from rest_framework.serializers import ModelSerializer
from .models import *
from user.serializers import *
from products.serializers import *
from user.serializers import *
class OrderLineSerializer(ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ["order","item","user","status","quantity_ordered"]


class TableSerializer(ModelSerializer):
    class Meta:
        model = Table
        fields = ["number","hourly_charge"]

class OrderSerailizer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["id","order_amount","table_number","user","order_date"]

class FetcbOrderSerailizer(ModelSerializer):
    table_number = TableSerializer()
    user = FetchUserSerializer()
    class Meta:
        model = Order
        fields = "__all__"

class FetchOrderSerializer(ModelSerializer):
    order = FetcbOrderSerailizer()
    user = FetchUserSerializer()
    class Meta:
        model = OrderLine
        fields = ["id","user","item","order","quantity_ordered","status","orderline_date"]

class FetchOrderlineDetailsSerializer(ModelSerializer):
    item = ItemSerializer()
    order = OrderSerailizer()
    class Meta:
        model = OrderLine
        fields = ["id","user","item","order","quantity_ordered","status",'orderline_date']

class FetchOrderLinesItemsSerializer(ModelSerializer):
    item = ItemSerializer()
    class Meta:
        model = OrderLine
        fields = ["id","user","item","quantity_ordered","status",'orderline_date']
