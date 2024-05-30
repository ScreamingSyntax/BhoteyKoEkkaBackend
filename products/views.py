from django.shortcuts import render
from rest_framework.views import APIView
from myproject.success import error_message, success_with_data, success_with_no_data,success_session_expiry
from products.models import Item,Category
from products.serializers import ItemSerializer,CategorySerializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework import serializers  
from products.serializers import *
from rest_framework import status
#Verification method
def field_verification(fields,data):
      for field in fields:
                    if field not in data:
                        return (error_message(f"Please input {field} while registering up"))
                    elif data[field] == "" or data[field] is None:

                        return (error_message( f"The field {field} cannot be empty."))
                    if(field=='item_price'):
                        try:
                              data['item_price']  = int (data['item_price'])  
                        except:
                              return (error_message( f"The item price must be Integer."))
                    if field =='category':
                        try:
                              data['category']  = int (data['category'])  
                        except:
                              return (error_message( f"The category must be Integer."))

class ViewCategoryProductsByName(APIView):
      authentication_classes = [SessionAuthentication,TokenAuthentication]
      def post(self,request):
            try:
                  object=Item.objects.all().order_by('-category__category_type').order_by('-item_name').exclude(is_delete = True)
                  if not request.user.is_authenticated:
                        return Response(success_session_expiry,status = status.HTTP_401_UNAUTHORIZED)
                  if 'category_name' not in request.data:
                        return Response(success_with_no_data("Please send category_name"))
                  if request.data['category_name'] == None or request.data['category_name'] == "":
                              serializers=ItemSerializer(object,many=True)
                              return Response(success_with_data(data=serializers.data))
                  #       return Response(success_with_no_data("Invalid Category Name"))
                  items = object.filter(category__category_name=request.data['category_name'])
                  items_serializer = ItemSerializer(items,many=True)
                  return Response(success_with_data(items_serializer.data))
            except Category.DoesNotExist:
                  return Response(error_message("The category doesn't exist"))
            
class CategoryView(APIView):
      authentication_classes = [SessionAuthentication,TokenAuthentication]
      def get(self, request,*args, **kwargs):
            if not request.user.is_authenticated:
                  return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
            food  = Category.objects.filter(category_type = 'Food').exclude(is_delete = True)
            bevrages = Category.objects.filter(category_type = 'Beverage').exclude(is_delete = True)
            food_serialier = CategorySerializer(food,many=True)
            bevrages_serialier = CategorySerializer(bevrages,many=True)
            return Response(success_with_data({
                  "food":food_serialier.data,
                  "beverage":bevrages_serialier.data
            }))

      def post(self,request,*args,**kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            try:
                  if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
                  if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
                  data=request.data
                  print(data)
                  serializer=CategorySerializer(data=data)
                  if serializer.is_valid():
                        serializer.save()
                        return Response(success_with_no_data("Category Added"))
                  return Response(error_message("Error adding category"))
            except serializers.ValidationError as validation_error:
                  return Response(field_verification(['category_name','category_type'],request.data))
            except:
                return Response(error_message("Something wen't wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      def patch(self, request, *args, **kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            item_id=request.data['id']
            try:
                  if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
                  if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
                  partial = kwargs.pop('partial', True)
                  item = Category.objects.get(pk=item_id)
                  serializer = CategorySerializer(item, data=request.data, partial=partial)
                  serializer.is_valid(raise_exception=True)
                  serializer.save()

                  return Response(success_with_data(serializer.data))
            except Category.DoesNotExist:
                  return Response(error_message('Item not found'), status=status.HTTP_404_NOT_FOUND)
            except serializers.ValidationError as validation_error:
                  
                  # return Response(request.data.keys(),status=status.HTTP_400_BAD_REQUEST)
                  return Response(field_verification(request.data.keys(),request.data),status=status.HTTP_400_BAD_REQUEST)
                  return Response(error_message(validation_error.detail), status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                  print(e)
                  return Response(error_message('Something went wrong'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


      def delete(self, request, *args, **kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            try:
                  if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
                  if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
                  item = Category.objects.get(pk=request.data['id'])
                  item.is_delete = True
                  item.save()

                  return Response(success_with_no_data("Item deleted successfully"))
            except Category.DoesNotExist:
                return Response(error_message(f"Item not found with id {request.data['id']}"))
            except Exception as e:
                print(e)
                return Response(error_message("Something wend wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Create     your views here.
class ItemView(APIView):
      authentication_classes = [SessionAuthentication,TokenAuthentication]
      def get(self, request,*args, **kwargs):
            if not request.user.is_authenticated:
                  return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
            object=Item.objects.all().exclude(is_delete = True)
            serializers=ItemSerializer(object,many=True)
            return Response(success_with_data(data=serializers.data))
            

      def post(self,request,*args,**kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
            if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
            data=request.data
            print(request.data)
            try:
                  serializer=AddItemSerializer(data=data)
                  if serializer.is_valid():
                        serializer.save()
                        return Response(success_with_no_data("Added product"))
                  print(serializer.errors)
                  return Response(error_message("Error adding product"))
            except serializers.ValidationError as validation_error:
                  return Response(field_verification(['item_name', 'item_price', 'category'],request.data))
            except Exception as e:
                print(e)
                return Response(error_message("Something wen't wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      def patch(self, request, *args, **kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            print(request.data)
            item_id=request.data['id']

            try:
                  if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
                  if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
                  partial = kwargs.pop('partial', True)
                  item = Item.objects.get(pk=item_id)
                  serializer = ItemSerializer(item, data=request.data, partial=partial)
                  serializer.is_valid(raise_exception=True)
                  serializer.save()

                  return Response(success_with_data(serializer.data))
            except Item.DoesNotExist:
                  return Response(error_message('Item not found'), status=status.HTTP_404_NOT_FOUND)
            except serializers.ValidationError as validation_error:
                  return Response(field_verification(request.data.keys(),request.data),status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                  print(e)
                  return Response(error_message('Something went wrong'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      def delete(self, request, *args, **kwargs):
            authentication_classes = [SessionAuthentication,TokenAuthentication]
            try:
                if not request.user.is_authenticated:
                        return Response(success_session_expiry(), status=status.HTTP_401_UNAUTHORIZED)
                if request.user.role != 'admin':
                        return error_message("You aren't allowed to do this action")
                item = Item.objects.get(pk=request.data['id'])
                item.is_delete = True
                item.save()

                return Response(success_with_no_data("Item deleted successfully"))
            except Item.DoesNotExist:
                return Response(error_message(f"Item not found with id {request.data['id']}"))
            except Exception as e:
                print(e)
                return Response(error_message("Something wend wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Create     your views here.