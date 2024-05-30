from django.urls import path
from .views import *
urlpatterns = [
    path('',UserMain.as_view()),
    path('login/',UserLogin.as_view()),
    path('changePass/',UserPassChange.as_view()),
    path('viewDetails/',UserAlongSideTables.as_view())
]
