from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings

import jwt
import boto3
from boto3.dynamodb.conditions import Key, Attr

from .pagination import MyPagination

newsapp_user = 'User'
news_table = 'News'
category_table = 'Category'
agency_table = 'Agency'
group_table = 'news_group'
secondary_news_table = 'secondary_news'  

# Create your views here.

aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
aws_region = settings.AWS_REGION

dynamodb = boto3.resource('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)

paginator = MyPagination()

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """
    API that will return all the news
    """
    category = dynamodb.Table(news_table).scan()['Items']
    page = paginator.paginate_queryset(category, request)
    return paginator.get_paginated_response(page)



class LoginView(APIView):
    """
    API for Login
    """
    @classmethod
    def post(cls, request):
        """
        POST API for login
        """
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        table = dynamodb.Table(newsapp_user)
        response = table.scan(FilterExpression=Key('username').eq(username))
        user = response['Items'][0]
        password = user['password']
        if password == data['password']:
            jwt_token = jwt.encode({'username': username}, settings.SECRET_KEY, algorithm='HS256')     
            context = {
                'user_id': user['id'],
                'user': user['username'],
                'email': user['email'],
                'first_name': user['firstName'],
                'last_name': user['lastName'],
                'jwt_token': jwt_token
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response({"Msg ': 'Invalid credentials "},status=status.HTTP_400_BAD_REQUEST)


class CategoryView(APIView):
    """
    API for Category
    """
    permission_classes = [AllowAny]
    @classmethod
    def get(cls, request):
        """
        GET API for Category
        """
        table = dynamodb.Table(category_table).scan()['Items']
        page = paginator.paginate_queryset(category, request)
        return Response(page, status=status.HTTP_200_OK)


class FeedByCategoryView(APIView):
    """
    API for Feed by Category
    """
    permission_classes = [AllowAny]
    @classmethod
    def get(cls, request, category_id):
        """
        GET API for Feed by Category
        """
        try:
            category_id = str(category_id)
            #fetching the news from the news table based on the category id
            table = dynamodb.Table(news_table).scan(
                        FilterExpression=Attr('category_id').eq(category_id) 
                    )['Items']
            page = paginator.paginate_queryset(table, request)
            return Response(page, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Msg ': 'Invalid category id "},status=status.HTTP_400_BAD_REQUEST)


class SecondaryNews(APIView):
    """
    API for Secondary News
    """
    permission_classes = [AllowAny]
    @classmethod
    def get(cls, request):
        """
        GET API for Secondary News
        """
        table = dynamodb.Table(secondary_news_table).scan()['Items']
        page = paginator.paginate_queryset(category, request)
        return Response(page, status=status.HTTP_200_OK)