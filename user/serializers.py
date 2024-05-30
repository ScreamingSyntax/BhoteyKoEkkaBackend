from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.hashers import make_password
from .models import *
class UserSerializer(ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ["user_name", "password", "role"]

class FetchUserSerializer(ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ["id","user_name", "role"]