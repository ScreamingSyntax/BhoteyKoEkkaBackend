from gettext import translation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth.hashers import make_password
from django.db import models
from .serializers import *
from myproject.success import *
from rest_framework import serializers 
from products.models import * 
from django.db.models import Count, Prefetch
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import viewsets
from django.db.models import F
from payment.models import Payment
class FetchTables(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self,request):
        if not request.user.is_authenticated:
            return Response(success_session_expiry)
        table = Table.objects.all()
        table_serialier = TableSerializer(table,many=True)
        return Response(success_with_data(table_serialier.data))

class TableOrderView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def post(self,request):
        try:
            if not request.user.is_authenticated:
                return Response(success_session_expiry())
            if request.user.role != "admin":
                return Response(error_message("You are not allowed for this action"))
            fields = ["number","hourly_charge"]
            for field in fields:
                if field not in request.data:
                    return Response(error_message(f"Field {field} missing"))
                data = request.data[field]
                if data == "" or data == None:
                    return Response(error_message(f"Field {field} cannot be null or empty"))
            table = Table.objects.filter(number = request.data["number"])
            if list(table) != []:
                return Response(error_message("Table already exists."))
            serializers = TableSerializer(data=request.data,many=False)
            if serializers.is_valid():
                serializers.save()
                return Response(success_with_no_data("Successfully Saved Table"))
            print(serializers.errors)
            return Response(error_message("Something wen't wrong"))
        except Exception as e:
            print(e)
            return Response(error_message("Something wen't wrong"))
    def patch(self,request):
        try:
            if not request.user.is_authenticated:
                return Response(success_session_expiry())
            if request.user.role != "admin":
                return Response(error_message("You are not allowed for this action"))
            if "number" not in request.data:
                return Response(error_message("Please add table number to the request"))
            print(request.data)
            table = Table.objects.get(number = request.data["number"])
            table_serializer = TableSerializer(instance = table,data=request.data,partial=True)
            if table_serializer.is_valid():
                table_serializer.save()
                return Response(success_with_no_data("Successfully Saved Table"))
            return Response(error_message("Something wen't wrong"))
        except Table.DoesNotExist:
            return Response(error_message("Table Doesn't Exist"))
        except: 
            return Response(error_message("Something wen't wrong"))
    def delete(self,request):
        try:
            if not request.user.is_authenticated:
                return Response(success_session_expiry())
            if request.user.role != "admin":
                return Response(error_message("You are not allowed for this action"))
            if "number" not in request.data:
                return Response(error_message("Please add table number to the request"))
            print(request.data)
            table = Table.objects.get(number = request.data["number"])
            table.delete()
            return Response(success_with_no_data("Successfully Deleted Table"))
        except Table.DoesNotExist:
            return Response(error_message("Table Doesn't Exist"))
        except: 
            return Response(error_message("Something wen't wrong"))
    def get(self,request):
        if request.user.is_authenticated:
            try:
                order_id = int(request.query_params.get('order', None))
                table_id = int(request.query_params.get('table', None))
                if order_id == None:
                    return Response(error_message("Please provide table id"))
                if table_id == None:
                    return Response(error_message("Please provide table id"))
                order_line = OrderLine.objects.filter(
                order_id=order_id,
                order__table_number=table_id,
                status__in=['pending', 'completed']   
                ).order_by('-order__order_date')
                order = Order.objects.get(id=order_id)
                table_serializer = TableSerializer(order.table_number)
                order_serializer = OrderSerailizer(order)
                order_line_serializer = FetchOrderlineDetailsSerializer(instance=order_line,many=True)
                return Response(success_with_data({
                    "order":order_serializer.data,
                    "table":table_serializer.data,
                    "orders" :order_line_serializer.data}))
            except Order.DoesNotExist:
                return Response(error_message("Order doesn't exist"))
            except Table.DoesNotExist:
                return Response(error_message("Table doesn't exist"))
            except Exception as e:
                print(e)
                return Response(error_message("Something wen't wrpmg"))
        else:
            return Response(success_session_expiry())

class MarkOrderCooked(APIView):
    def post(self,request):
            data = request.data
            if 'id' not in data:
                return Response(error_message("OrderLine id is missing"))
                # Validate 'id' and convert to integer
            orderline_id = int(data['id'])
            orderline = OrderLine.objects.get(id=orderline_id)
            if orderline.status == "completed":
                return Response(error_message("The order is already completed cannot remove"))
            if orderline.status == 'cancelled':
                return Response(error_message("The orderline is already cancelled"))
            orderline.status = 'completed'
            orderline.save() 
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        'type': 'orderline_update_message',
                        'message': 'Order line cancelled successfully',
                    }
                )
            async_to_sync(channel_layer.group_send)(
                "table_order_updates",
                {
                    "type": "table_order_update_message",  # This should match the method name in the consumer
                }
            )
        
            return Response(success_with_no_data("Done"))
# class TableViewSet(viewsets.ModelViewSet):
#     authentication_classes = [SessionAuthentication, TokenAuthentication]
#     # def get(self,request)
    # def post(lsef)
class DeliveryOrder(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def post(self, request):
            if not request.user.is_authenticated:
                return Response(success_session_expiry())
        # try:
            orderItems = request.data.get("orderItems", [])
            if not orderItems:
                return Response(error_message("Please send orderItems"))
            total_order_amount = 0
            order = Order.objects.create(
                    order_amount=0,
                    user=request.user,
                    type='delivery'
                )
            for data in orderItems:
                item_id = data.get('item_id')
                quantity = data.get('quantity')
                if not all([item_id, quantity]):
                    return Response(error_message("Missing item_id, quantity"))
                try:
                    item = Item.objects.get(id=item_id)
                except Item.DoesNotExist:
                    return Response(error_message(f"Item with id {item_id} does not exist"))
                total_price = item.item_price * quantity
                total_order_amount += total_price
                order.order_amount = total_order_amount
                order.is_paid = True
                order.save()
                OrderLine.objects.create(
                        order=order,
                        item_id=data['item_id'],
                        user=request.user,
                        status='completed',
                        quantity_ordered=data['quantity']
                    )
            Payment.objects.create(
                    order = order,
                    total_amount = total_order_amount,
                    added_by = request.user
                ).save()
            return Response(success_with_no_data("Successfully Placed Delivery"))
        # except Exception as e:
        #     print(e.error_message())
        #     return Response(error_message("Something went wrong"))

class OrderView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request):
        if request.user.is_authenticated:
            print("Suyog")
            orders_obj = OrderLine.objects.filter(
                order__is_cancelled=False, 
                status__in=['pending', 'completed'] 
            ).exclude(order__is_paid=True).order_by('-orderline_date')
            order_data = {}
            for order in orders_obj:
                order_serialized = FetchOrderlineDetailsSerializer(instance=order)
                table_number = order.order.table_number.number
                order_data.setdefault(table_number, [])
                order_data[table_number].append(order_serialized.data)
            return Response(success_with_data(order_data))
        else:
            return Response(success_session_expiry())
        
    def delete(self, request):
        if request.user.is_authenticated:
            data = request.data
            print(data)
            try:
                if 'id' not in data:
                    return Response(error_message("OrderLine id is missing"))
                orderline_id = int(data['id'])
                print(orderline_id)
                orderline = OrderLine.objects.get(id=orderline_id)
                order= Order.objects.filter(id=orderline.order.id)
                if order[0].is_paid:
                    return Response(error_message("The order is already paid cannot remove"))
                if orderline.status == "completed":
                    return Response(error_message("The order is already completed cannot remove"))
                if orderline.status == 'cancelled':
                    return Response(error_message("The orderline is already cancelled"))
                orderline.status = 'cancelled'
                orderline.save()
                total_price = sum(line.item.item_price * line.quantity_ordered for line in orderline.order.orderline_set.filter(status__in=['pending', 'completed']))
                order_line = OrderLine.objects.filter(order = order[0]).exclude(status='cancelled')
                if list(order_line) == []:
                    order.update(is_cancelled=True,order_amount=0)
                    return Response(success_with_no_data("All the orders are cancelled"))
                order.update(order_amount=total_price)
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        'type': 'orderline_update_message',
                        'message': 'Order line cancelled successfully',
                    }
                )
                async_to_sync(channel_layer.group_send)(
                "table_order_updates",
                {
                    "type": "table_order_update_message",  # This should match the method name in the consumer
                }
            )   
                print("One")
                return Response(success_with_data({"message": "Order line cancelled successfully", "total_price": total_price}))
            except OrderLine.DoesNotExist:
                print("Two")
                return Response(error_message("The orderline doesn't exist"))
            except ValueError:
                print("Thee")
                return Response(error_message("Invalid orderline ID"))
            except Exception as e:
                print("Four")
                return Response(error_message(f"Something went wrong: {str(e)}"))
        else:
            print("Fice ")
            return Response(success_session_expiry())

            
    def patch(self, request):
        if request.user.is_authenticated:
            data = request.data
            try:
                if 'id' not in data or 'quantity' not in data:
                    return Response(error_message("OrderLine id or Quantity Missing"))
                # Validate 'id' and 'quantity', then convert to integers
                orderline_id = int(data['id'])
                quantity = int(data['quantity'])
                orderline = OrderLine.objects.get(id=orderline_id)
                
                # Check if the order line or its related order is paid or cancelled
                if orderline.order.is_paid or orderline.status == 'cancelled' or orderline.order.is_cancelled:
                    return Response(error_message("Cannot update a paid or cancelled order line"))
                
                orderline.quantity_ordered = quantity
                orderline.save()
                
                # Update total_price calculation to use the status field
                total_price = sum(line.item.item_price * line.quantity_ordered for line in orderline.order.orderline_set.filter(status__in=['pending', 'completed']))
                Order.objects.filter(id=orderline.order.id).update(order_amount=total_price)

                # Send WebSocket message
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        'type': 'orderline_update_message',
                        'message': 'Order line updated successfully',
                    }
                )

                return Response({"message": "Order line updated successfully", "total_price": total_price})
            except OrderLine.DoesNotExist:
                return Response(error_message("The orderline doesn't exist"))
            except ValueError:
                return Response(error_message("Invalid input"))
            except Exception as e:
                return Response(error_message(f"Something went wrong: {str(e)}"))
        else:
            return Response(success_session_expiry())

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(error_message("User Not Authenticated"))

        try:
            print(request.data)
            orderItems = request.data.get("orderItems", [])
            if not orderItems:
                return Response(error_message("Please send orderItems"))

            total_order_amount = 0
            table_number = None
            order_id = 0
            order_exists = False
            for data in orderItems:
                item_id = data.get('item_id')
                quantity = data.get('quantity')
                table_number_input = data.get('table')
                order = Order.objects.filter(table_number__number=table_number_input,is_cancelled=False,is_paid=False)
                if list(order) != []:
                    order_id = order[0].id
                    order_exists = True
                if not all([item_id, quantity, table_number_input]):
                    return Response(error_message("Missing item_id, quantity, or table"))

                try:
                    print("da")
                    item = Item.objects.get(id=item_id)
                    table = Table.objects.get(number=table_number_input)
                except Item.DoesNotExist:
                    return Response(error_message(f"Item with id {item_id} does not exist"))
                except Table.DoesNotExist:
                    return Response(error_message(f"Table with number {table_number_input} does not exist"))

                table_number = table.pk

                total_price = item.item_price * quantity
                total_order_amount += total_price
            if not order_exists:
                order = Order.objects.create(
                    order_amount=total_order_amount,
                    table_number_id=table_number,
                    user=request.user
                )

                for data in orderItems:
                    OrderLine.objects.create(
                        order=order,
                        item_id=data['item_id'],
                        user=request.user,
                        status='pending',
                        quantity_ordered=data['quantity']
                    )
            if order_exists:
                print("da")

                order = Order.objects.get(id=order_id)
                print("da")

                order.order_amount += total_order_amount
                order.save()

                for data in orderItems:
                    OrderLine.objects.create(
                        order=order,
                        item_id=data['item_id'],
                        user=request.user,
                        status='pending',
                        quantity_ordered=data['quantity']
                    )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        'type': 'orderline_update_message',
                        'message': 'Order line cancelled successfully',
                    }
                )
            async_to_sync(channel_layer.group_send)(
                "table_order_updates",
                {
                    "type": "table_order_update_message",  # This should match the method name in the consumer
                }
            )

            return Response(success_with_no_data("Successfully Placed Order"))
        except Exception as e:
            print(e)
            return Response(error_message("Something went wrong"))
