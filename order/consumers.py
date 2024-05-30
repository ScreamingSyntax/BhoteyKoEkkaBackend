
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import OrderLine
import json
from django.db.models import F
from order.models import *
from django.core.serializers.json import DjangoJSONEncoder

class OrderLineConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("order_updates", self.channel_name)
        await self.send_updates()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("order_updates", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    @database_sync_to_async
    def get_orderlines(self):

        orderlines = OrderLine.objects.filter(status__in=['pending'], order__is_paid=False).annotate(item_name=F('item__item_name')).values('id','item_name', 'quantity_ordered', 'status','orderline_date')
        return list(orderlines)
    async def send_updates(self):
        orderlines = await self.get_orderlines()
    # Convert `datetime` fields to string using DjangoJSONEncoder
        orderlines_converted = json.loads(json.dumps(orderlines, cls=DjangoJSONEncoder))
        await self.send(text_data=json.dumps({
            'type': 'orderline_updates',
            'message': orderlines_converted
        }))

    async def orderline_update_message(self, event):
        await self.send_updates()


class TableOrderConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("table_order_updates", self.channel_name)
        await self.send_table_order_updates()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("table_order_updates", self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    @database_sync_to_async
    def get_order_data(self):
        orders = Order.objects.filter(is_cancelled=False, is_paid=False)
        print(f"The orders are {orders}")
        order_data = {}
        for order in orders:
            order_lines = order.orderline_set.filter(status__in=['pending', 'completed'])
            for line in order_lines:
                table_number = order.table_number.number
                if table_number not in order_data:
                    order_data[table_number] = []
                order_data[table_number].append({
                    'id':order.id,
                    'item_name': line.item.item_name,
                    'quantity_ordered': line.quantity_ordered,
                    'status': line.status,
                    'order_line_id':line.id,
                    'table_number':order.table_number.number,
                    'order_date':str(line.orderline_date)
                })
        return order_data

    async def send_table_order_updates(self):
        order_data = await self.get_order_data()
        await self.send(text_data=json.dumps({
            'type': 'table_order_updates',
            'message': order_data
        }))

    async def table_order_update_message(self, event):
        # Handler to trigger updates
        await self.send_table_order_updates()
