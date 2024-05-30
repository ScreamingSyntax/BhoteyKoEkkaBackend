from django.contrib import admin

from products.models import Category, Item

# Register your models here.
admin.site.register(Item)
admin.site.register(Category)
