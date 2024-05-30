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
from order.serializers import TableSerializer 
from order.models import Table
class UserMain(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    def get(self,request):
        if request.user.is_authenticated:
            query_set = BaseUser.objects.all()
            serializer_class = FetchUserSerializer(query_set,many=True)
            return Response(serializer_class.data)
        else:
            return Response(success_session_expiry())
    def delete(self,request):
        try:
            if not request.user.is_authenticated:
                return Response(success_session_expiry())
            if request.user.role != "admin":
                return Response(error_message("You are not allowed for this action."))
            # base_user = BaseUser.objects.get(user)
            if 'user_name' not in request.data:
                return Response(error_message("User name not in request"))
            if request.data['user_name'] == "" or request.data['user_name'] == None:
                return Response(error_message("User name canot be null or empty"))
            base_user = BaseUser.objects.get(user_name = request.data['user_name'])
            base_user.delete()
            return Response(success_with_no_data("User Deleted"))
        except BaseUser.DoesNotExist:
            return Response(error_message("The user doesn't exist"))
        except:
            return Response(error_message("Something wen't wrong"))
    
    def patch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                if 'id' not in request.data:
                    return Response(error_message("Please send id to update"))
                if 'role' in request.data and request.data['role'] not in dict(BaseUser.USER_TYPES).keys():
                    return Response(error_message("Invalid role provided"), status=status.HTTP_400_BAD_REQUEST)
                id = request.data['id']
                instance = BaseUser.objects.get(id=id)
                serializer = FetchUserSerializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                user_data = serializer.validated_data
                serializer.save()
                return Response(success_with_no_data("Successfully Updated User"), status=status.HTTP_200_OK)

            except BaseUser.DoesNotExist:
                return Response(error_message("User not found"), status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                print(e)
                return Response(error_message("Something went wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(success_session_expiry())

    def post(self, request):
        if request.user.is_authenticated:    
            try: 
                if request.data['role'] not in dict(BaseUser.USER_TYPES).keys():
                    return Response(error_message("Invalid role provided"), status=status.HTTP_400_BAD_REQUEST)

                existing_user = BaseUser.objects.filter(user_name= request.data['user_name'])
                if list(existing_user) != []:
                    return Response(error_message("The member already exists."))
                serializer = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                user_data = serializer.validated_data
                user_data['password'] = make_password(user_data['password'])

                if BaseUser.objects.filter(user_name=user_data['user_name']).exists():
                    return Response(error_message("User Already Exists"), status=status.HTTP_400_BAD_REQUEST)

                BaseUser.objects.create(**user_data)
                return Response(success_with_no_data("Successfully Added User"), status=status.HTTP_201_CREATED)
            
            except serializers.ValidationError as validation_error:
            
                for field in ["user_name", "password", "role"]:
                    if field not in request.data:
                        return Response(error_message(f"Please input {field} while registering up"))
                    elif request.data[field] == "" or request.data[field] is None:
                        return Response(error_message( f"The field {field} cannot be empty."))

            except Exception as e:
                print(e)
                return Response(error_message("Something wen't wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response(success_session_expiry())

class UserPassChange(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    def post(self,request):
        try:
            if request.user.is_authenticated:
                if request.user.role != "admin":
                    return Response(error_message("You aren't allowed for this action"))
                for field in ["current_password", "new_password",'user_name']:
                    if field not in request.data:
                        return Response(error_message(f"Please input {field} to change pass "))
                    elif request.data[field] == "" or request.data[field] is None:
                        return Response(error_message( f"The field {field} cannot be empty."))
                user = BaseUser.objects.get(user_name = request.data['user_name'])
                if not user.check_password(request.data["current_password"]):
                    return Response(error_message("The old password doesn't match"))
                new_pass = make_password(request.data['new_password'])
                user.password = new_pass
                user.save()
                return Response(success_with_data("Successfully Changed password"))
        except Exception as e:
            print(e)
            return Response(success_session_expiry())
        except BaseUser.DoesNotExist:
            return Response(success_with_no_data("The base user doesn't exist."))

class UserLogin(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    def post(self, request):
            
        try:
            user = BaseUser.objects.get(user_name= request.data.get('user_name'))
            if not user.check_password(request.data.get("password")):
                return Response(error_message("Invalid credentials"))
            token, created = Token.objects.get_or_create(user=user)
            serializer = FetchUserSerializer(instance=user)
            return Response(success_with_data({
                "success": 1,
                "token": token.key,
                "data": serializer.data,
                "message": "Successfully Logged In"
            }))
        except BaseUser.DoesNotExist:
            return Response(error_message("The user doesn\'t exist"))
        except serializers.ValidationError as validation_error:
            error_messages = []
            for field in ["user_name", "password"]:
                if field not in request.data:
                    return Response(error_message(f"Please input {field} while login "))
                elif request.data[field] == "" or request.data[field] is None:
                    return Response(error_message( f"The field {field} cannot be empty."))
            return Response(error_message(validation_error.detail), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(error_message("Something went wrong"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAlongSideTables(APIView):
    authentication_classes = [SessionAuthentication,TokenAuthentication]
    def get(self,request):
        user = BaseUser.objects.all().exclude(role='admin')
        table = Table.objects.all()
        user_serializer = FetchUserSerializer(user,many=True)
        table_serializer = TableSerializer(table,many=True)
        return Response(success_with_data({'user':user_serializer.data,'table':table_serializer.data}))
