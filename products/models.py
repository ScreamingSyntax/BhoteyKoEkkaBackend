from django.db import models

# Create your models here.
class Category(models.Model):
      category_type=models.CharField(max_length=255,blank=False)
      category_name=models.CharField(max_length=255,blank=False)
      is_delete = models.BooleanField(default = False)
      def __str__(self):
            return self.category_name  + f" {self.id}"# Change 'email' to 'user_name'

class Item(models.Model):
      item_name=models.CharField(max_length=255,blank=False)
      item_price=models.IntegerField(blank=False)
      category=models.ForeignKey(Category,max_length=255,blank=False,on_delete=models.CASCADE,)
      is_delete = models.BooleanField(default = False)

      def __str__(self):
            return self.item_name + f" {self.id}"  # Change 'email' to 'user_name'
