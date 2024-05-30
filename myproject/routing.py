# myproject/routing.py
from django.urls import path
from order.consumers import *

websocket_urlpatterns = [
    
    path('ws/order/kitchen/', OrderLineConsumer.as_asgi()),
    path('ws/order/staff/', TableOrderConsumer.as_asgi()),

]