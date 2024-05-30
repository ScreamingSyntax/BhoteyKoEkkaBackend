from rest_framework import serializers
from .models import Category, Item

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields ='__all__'


class AddItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'    
class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Item
        fields = '__all__'
