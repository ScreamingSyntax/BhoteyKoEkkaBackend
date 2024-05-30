from django.urls import path
from .views import *
urlpatterns = [
    path('category/',CategoryView.as_view()),
    path('item/',ItemView.as_view()),
    path('byCategory/',ViewCategoryProductsByName.as_view())
]
