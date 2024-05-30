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
from .serializers import *
from django.utils import timezone 
from django.db.models import Sum, Q
from datetime import timedelta
from django.utils.dateparse import parse_date
from order.models import *
from order.serializers import *
from user.serializers import *
from django.utils import timezone
from datetime import datetime
import math 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import F
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

class RecentPaymentHistory(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request):
        if request.user.is_authenticated:
            try:
                payments = Payment.objects.order_by('-id')[:10]
                serializer = AllPaymentSerializer(payments, many=True)
                return Response(success_with_data(serializer.data))
            except Exception as e:
                print(e)
                return Response(error_message("Something went wrong"))
        else:
            return Response(success_session_expiry())

class PaymentHistory(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def get(self, request, history_type):
        if not request.user.is_authenticated:
            return Response(success_session_expiry())
        print(f"This is history type {history_type}")

        if history_type == 'daily':
            print("Here")
            return self.get_daily_history(request)
        elif history_type == 'weekly':
            return self.get_weekly_history(request)
        elif history_type == 'monthly':
            return self.get_monthly_history(request)
        elif history_type == 'custom':
            return self.get_custom_range_history(request)
        else:
            return Response(error_message("Something wen't wrong"))

    def get_custom_range_history(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not start_date or not end_date:
            return Response(error_message("Both start_date and end_date must be provided"))
        try:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            if start_date > end_date:
                return Response(error_message("start_date must be before end_date"))
        except ValueError:
            return Response(error_message( "Invalid date format"))

        payments = Payment.objects.filter(date_time__date__range=[start_date, end_date]).order_by('-date_time')
        serializer = PaymentSerializer(payments, many=True)
        return Response(success_with_data(serializer.data))

    def get_daily_history(self, request):
        date = request.query_params.get('date')
        print(f"This is the date {date}")
        if not date:
            today = timezone.now().date()
            payments = Payment.objects.filter(date_time__date=today).order_by('-date_time')
            serializer = PaymentSerializer(payments, many=True)
            return Response(success_with_data(serializer.data))

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            # print(date)
            payments = Payment.objects.filter(date_time__date=date).order_by('-date_time')
            serializer = PaymentSerializer(payments, many=True)
            # print(serializer.data)
            return Response(success_with_data( serializer.data))
        except ValueError:
            return Response(error_message("Please provide valid date in 'YYYY-MM-DD' format."))
        
    def get_weekly_history(self, request):
        if request.user.role != 'admin':
            return error_message("You aren't allowed to do this action")
        today = timezone.now().date()
        week_start = today - timedelta(days=(today.weekday() + 1) % 7)  # Shift to Sunday as start
        week_end = week_start + timedelta(days=6)

        payments = Payment.objects.filter(date_time__date__range=[week_start, week_end]).order_by('-date_time')
        serializer = PaymentSerializer(payments, many=True)

        return Response(success_with_data(serializer.data))
    def get_monthly_history(self, request):
        if request.user.role != 'admin':
            return error_message("You aren't allowed to do this action")
        today = timezone.now()
        month_start = today.replace(day=1).date()
        next_month = today.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)
        payments = Payment.objects.filter(date_time__date__range=[month_start, month_end]).order_by('-date_time')
        serializer = PaymentSerializer(payments, many=True)
        return Response(success_with_data( serializer.data))

class ParticularPaymentView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def post(self,request):
        if not request.user.is_authenticated:
            return Response(error_message("User Not Authenticated"))
        if 'order_id' not in request.data:
            return Response(error_message("Please enter order id"))
        if request.data['order_id'] == None or type(request.data['order_id']) == str:
            return Response(error_message("Invalid order id"))
        try:
            id = request.data['order_id']
            order_id = Order.objects.get(id=id)
            if order_id.is_paid == False:
                return Response(error_message("The order isn't paid yet"))
            payment = Payment.objects.filter(order=order_id)
            payment_serailizer = PaymentSerializer(instance=payment[0])
            order_serializer = FetcbOrderSerailizer(instance = payment[0].order)
            order_lines = OrderLine.objects.filter(order= payment[0].order).filter(status='completed')
            order_lines_serializer = FetchOrderLinesItemsSerializer(order_lines,many=True)
            return Response(success_with_data({
                "payment_details":payment_serailizer.data,
                "order_details":order_serializer.data,
                "order_line_details":order_lines_serializer.data
            }))
        except Order.DoesNotExist:
            return Response(error_message("The order doesn't exist"))
        except Exception as e:
            print(f"The exception iis {e}")
            return Response(error_message("Something wen't wrong"))
        
class PaymentView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self,request):
        if request.user.is_authenticated:
            try:
                payment_id = int(request.query_params.get('payment_id', None))
                if payment_id == None:
                    return Response(error_message("Please provide payment id"))
                payment = Payment.objects.get(id=payment_id)
                payment_serializer = PaymentSerializer(payment)
                order_line = OrderLine.objects.filter(order=payment.order)
                order_line_serializer = FetchOrderlineDetailsSerializer(order_line,many=True)
                table_serializer = TableSerializer(payment.order.table_number)
                order_serializer = OrderSerailizer(payment.order)
                user_serializer = UserSerializer(payment.order.user)
                return Response(
                    success_with_data({
                        "user":user_serializer.data,
                        "table": table_serializer.data,
                        "order":order_serializer.data,
                        "order_line":order_line_serializer.data,
                        "payment":payment_serializer.data
                    })
                )
            except Payment.DoesNotExist:
                return Response(error_message("Payment doesn't exist"))
            except Exception as e: 
                print(e)
                return  Response(error_message("Something wen't wrong"))
        else:
            return Response(success_session_expiry())
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(error_message("User not authenticated"))
        try:
            print(request.data)

            required_fields = ['customer_name', 'order']
            for field in required_fields:
                if field not in request.data or not request.data[field]:
                    return Response(error_message(f"The field {field} should be provided and cannot be empty"))
            if 'customer_phone' in request.data and not request.data['customer_phone']:
                return Response(error_message("Customer Phone is invalid"))
            order_id = request.data['order']
            order = Order.objects.get(id=order_id)
            now = timezone.now()
            table_cost = Table.objects.get(number=order.table_number.number).hourly_charge
            first_order_time = order.order_date
            time_spent = (now - first_order_time).total_seconds() / 3600
            request.data['added_by'] = request.user.id
            channel_layer = get_channel_layer()
            OrderLine.objects.filter(order=order).exclude(status='cancelled').update(status='completed')
            rounded_hours = math.ceil(time_spent)
            print(rounded_hours)
            total_amount = (table_cost * rounded_hours) + order.order_amount
            request.data['total_amount'] = total_amount
            print(f"The order is {request.data}")
            payment_serializer = PayemntSerializerToAdd(data=request.data)
            if payment_serializer.is_valid():          
                async_to_sync(channel_layer.group_send)(
                        "order_updates",
                        {
                            'type': 'orderline_update_message',
                            'message': 'Paid for the order',
                        }
                    )
                async_to_sync(channel_layer.group_send)(
                    "table_order_updates",
                    {
                        "type": "table_order_update_message",  # This should match the method name in the consumer
                    }
            )
                payment_serializer.save()   
                order.is_paid = True
                order.save()
                return Response(success_with_data(payment_serializer.data))

            return Response(error_message(payment_serializer.errors))

        except Order.DoesNotExist:
            print("This is a exception")
            return Response(error_message("Order doesn't exist"))
        except Exception as e:
            print(e)
            return Response(error_message(str(e)))



class CategoryItemPopularityView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self,request):
        if not request.user.is_authenticated:
            return Response(success_session_expiry())
        item_sales = OrderLine.objects.filter(item__category__category_type = 'Food').values('item__category__category_name', 'item__item_name') \
        .annotate(total_sales=Sum('quantity_ordered')) \
        .order_by('-total_sales')[:10] 

        item_categories = [data['item__category__category_name'] for data in item_sales]
        items_name = [data['item__item_name'] for data in item_sales]
        item_sales_count = [data['total_sales'] for data in item_sales]
        

        bevrages_sales = OrderLine.objects.filter(item__category__category_type = 'Beverage').values('item__category__category_name', 'item__item_name') \
        .annotate(total_sales=Sum('quantity_ordered')) \
        .order_by('-total_sales')[:10] 
        bevrages_categories = [data['item__category__category_name'] for data in bevrages_sales]
        bevrages_name = [data['item__item_name'] for data in bevrages_sales]
        bevrages_sales_count = [data['total_sales'] for data in bevrages_sales]


        return Response({
            'success':1,
            'data':{
                'item_sales_data' :{
                    'categories': item_categories,
                    'items': items_name,
                    'sales': item_sales_count,
                },
                'bevrages_sales_data':{
                    'categories': bevrages_categories,
                    'items': bevrages_name,
                    'sales': bevrages_sales_count,
                }
            }
        })


class OrderTypeDistributionView(APIView):
    def get(self, request, history_type):
        if not request.user.is_authenticated:
            return Response({'success': 0, 'message': 'User not authenticated'})

        if history_type == 'daily':
            return self.get_daily_distribution(request)
        elif history_type == 'weekly':
            return self.get_weekly_distribution(request)
        elif history_type == 'monthly':
            return self.get_monthly_distribution(request)
        elif history_type == 'custom':
            return self.get_custom_range_distribution(request)
        else:
            return Response({'success': 0, 'message': "Invalid history type"})

    def aggregate_orders(self, annotation):
        return Order.objects.annotate(period=annotation('order_date')) \
                            .values('period', 'type') \
                            .annotate(total_orders=Count('id')) \
                            .order_by('period', 'type')
    

# class OrderTypeDistributionView(APIView):
#     authentication_classes = [SessionAuthentication, TokenAuthentication]

#     def get(self, request, history_type):
#         if not request.user.is_authenticated:
#             return Response({'success': 0, 'message': 'User not authenticated'})
#         if request.user.role != 'admin':
#             return error_message("You aren't allowed to do this action")
#         if history_type == 'daily':
#             return self.get_daily_distribution(request)
#         elif history_type == 'weekly':
#             return self.get_weekly_distribution(request)
#         elif history_type == 'monthly':
#             return self.get_monthly_distribution(request)
#         elif history_type == 'custom':
#             return self.get_custom_range_distribution(request)
#         else:
#             return Response({'success': 0, 'message': "Invalid history type"})

#     def aggregate_sales_data(self, start_date, end_date=None):
#         end_date = end_date or start_date
#         item_sales = OrderLine.objects.filter(
#             item__category__category_type='Food',
#             order__order_date__date__range=[start_date, end_date]
#         ).exclude(status='cancelled').values('item__category__category_name', 'item__item_name') \
#          .annotate(total_sales=Sum('quantity_ordered')) \
#          .order_by('-total_sales')[:10]
        
#         beverage_sales = OrderLine.objects.filter(
#             item__category__category_type='Beverage',
#             order__order_date__date__range=[start_date, end_date]
#         ).exclude(status='cancelled').values('item__category__category_name', 'item__item_name') \
#         .annotate(total_sales=Sum('quantity_ordered')) \
#         .order_by('-total_sales')[:10]

#         return {
#             'item_sales_data': {
#                 'items': [data['item__item_name'] for data in item_sales],
#                 'sales': [data['total_sales'] for data in item_sales],
#             },
#             'beverage_sales_data': {
#                 'items': [data['item__item_name'] for data in beverage_sales],
#                 'sales': [data['total_sales'] for data in beverage_sales],
#             },
#         }

#     def aggregate_orders_and_revenue(self, annotation, start_date, end_date=None):
#         end_date = end_date or start_date
#         return Order.objects.filter(
#             order_date__date__range=[start_date, end_date], is_paid=True
#         ).annotate(period=annotation('order_date')).values('period') \
#           .annotate(total_orders=Count('id'), total_revenue=Sum('order_amount')) \
#           .order_by('period')

#     def get_daily_distribution(self, request):
#         date_param = request.query_params.get('date')
#         if date_param:
#             try:
#                 date = datetime.strptime(date_param, '%Y-%m-%d').date()
#             except ValueError:
#                 return Response({'success': 0, 'message': "Invalid date format"})
#         else:
#             date = timezone.now().date()

        # orders_and_revenue = self.aggregate_orders_and_revenue(TruncDay, date)
#         sales_data = self.aggregate_sales_data(date)

#         return Response({'success': 1, 'data': {'order_distribution': list(orders_and_revenue), **sales_data}})

#     def get_weekly_distribution(self, request):
#         today = timezone.now().date()
#         week_start = today - timedelta(days=(today.weekday() + 1) % 7)
#         week_end = week_start + timedelta(days=6)
#         orders_and_revenue = self.aggregate_orders_and_revenue(TruncWeek, week_start, week_end)
#         sales_data = self.aggregate_sales_data(week_start, week_end)
#         return Response({'success': 1, 'data': {'order_distribution': list(orders_and_revenue), **sales_data}})

#     def get_monthly_distribution(self, request):
#         today = timezone.now()
#         month_start = today.replace(day=1).date()
#         next_month = today.replace(day=28) + timedelta(days=4)
#         month_end = next_month - timedelta(days=next_month.day)
#         orders_and_revenue = self.aggregate_orders_and_revenue(TruncMonth, month_start, month_end)
#         sales_data = self.aggregate_sales_data(month_start, month_end)
#         return Response({'success': 1, 'data': {'order_distribution': list(orders_and_revenue), **sales_data}})

#     def get_custom_range_distribution(self, request):
#         start_date_param = request.query_params.get('start_date')
#         end_date_param = request.query_params.get('end_date')
#         start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
#         end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
#         orders_and_revenue = self.aggregate_orders_and_revenue(TruncDay, start_date, end_date)
#         sales_data = self.aggregate_sales_data(start_date, end_date)
#         return Response({'success': 1, 'data': {'order_distribution': list(orders_and_revenue), **sales_data}})
    

class OrderTypeDistributionView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self, request, history_type):
        if not request.user.is_authenticated:
            return Response({'success': 0, 'message': 'User not authenticated'})
        if history_type == 'daily':
            return self.get_daily_distribution(request)
        elif history_type == 'weekly':
            return self.get_weekly_distribution(request)
        elif history_type == 'monthly':
            return self.get_monthly_distribution(request)
        elif history_type == 'custom':
            return self.get_custom_range_distribution(request)
        else:
            return Response(success_session_expiry())
    
    def aggregate_orders_and_revenue(self, annotation, start_date, end_date=None):
        end_date = end_date or start_date
        return Order.objects.filter(
            order_date__date__range=[start_date, end_date], is_paid=True
        ).annotate(period=annotation('order_date')).values('period') \
          .annotate(total_orders=Count('id'), total_revenue=Sum('order_amount')) \
          .order_by('period')
    
    def aggregate_orders(self, annotation):
        return Order.objects.filter(is_paid=True).annotate(period=annotation('order_date')) \
                            .values('period', 'type') \
                            .annotate(total_orders=Count('id')) \
                            .order_by('period', 'type')


    def aggregate_sales_data(self, start_date, end_date=None):
        end_date = end_date or start_date
        item_sales = OrderLine.objects.filter(
            item__category__category_type='Food',
            order__order_date__date__range=[start_date, end_date]
        ).exclude(status='cancelled').values('item__category__category_name', 'item__item_name') \
         .annotate(total_sales=Sum('quantity_ordered')) \
         .order_by('-total_sales')[:10]
        
        beverage_sales = OrderLine.objects.filter(
            item__category__category_type='Beverage',
            order__order_date__date__range=[start_date, end_date]
        ).exclude(status='cancelled').values('item__category__category_name', 'item__item_name') \
        .annotate(total_sales=Sum('quantity_ordered')) \
        .order_by('-total_sales')[:10]

        return {
            'item_sales_data': {
                'items': [data['item__item_name'] for data in item_sales],
                'sales': [data['total_sales'] for data in item_sales],
            },
            'beverage_sales_data': {
                'items': [data['item__item_name'] for data in beverage_sales],
                'sales': [data['total_sales'] for data in beverage_sales],
            },
        }

    def get_daily_distribution(self, request):
        date_param = request.query_params.get('date')
        print(date_param)
        if date_param:
            try:
                date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(error_message("Invalid date format"))
        else:
            date = timezone.now().date()
        orders_and_revenue = self.aggregate_orders_and_revenue(TruncDay, date)
        # print(orders_and_revenue)\
        period = []
        if list(orders_and_revenue) != []:
            period = list(orders_and_revenue)[0]
        orders = self.aggregate_orders(TruncDay).filter(order_date__date=date)
        sales_data = self.aggregate_sales_data(date)
        return Response(success_with_data({'order_distribution':list(orders),'period':period,**sales_data}))

    def get_weekly_distribution(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        orders_and_revenue = self.aggregate_orders_and_revenue(TruncWeek, week_start, week_end)
        period = []
        if list(orders_and_revenue) != []:
            period = list(orders_and_revenue)[0]
        orders = self.aggregate_orders(TruncWeek).filter(order_date__date__range=[week_start, week_end])
        sales_data = self.aggregate_sales_data(week_start, week_end)

        return Response(success_with_data({'order_distribution':list(orders),'period':period,**sales_data}))

    def get_monthly_distribution(self, request):
        today = timezone.now()
        month_start = today.replace(day=1).date()
        next_month = today.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)
        orders_and_revenue = self.aggregate_orders_and_revenue(TruncMonth, month_start, month_end)
        period = []
        if list(orders_and_revenue) != []:
            period = list(orders_and_revenue)[0]
        orders = self.aggregate_orders(TruncMonth).filter(order_date__date__range=[month_start, month_end])
        sales_data = self.aggregate_sales_data(month_start, month_end)

        return Response(success_with_data({'order_distribution':list(orders),'period':period,**sales_data}))

    def get_custom_range_distribution(self, request):
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        if not start_date_param or not end_date_param:
            return Response(error_message( "Both start_date and end_date must be provided"))
        try:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        except ValueError:
            return Response(error_message( "Invalid date format"))

        if start_date > end_date:
            return Response(error_message("Start_date must be before end_date"))
        orders_and_revenue = self.aggregate_orders_and_revenue(TruncDay, start_date, end_date)
        period = []
        if list(orders_and_revenue) != []:
            period = list(orders_and_revenue)[0]
        orders = self.aggregate_orders(TruncDay).filter(order_date__date__range=[start_date, end_date])
        sales_data = self.aggregate_sales_data(start_date, end_date)

        return Response(success_with_data({'order_distribution':list(orders),'period':period,**sales_data}))
