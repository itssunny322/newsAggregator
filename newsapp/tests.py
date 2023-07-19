from django.test import TestCase
import unittest
from django.test import Client

from .models import News, Category
from .view import home, LoginView, CategoryView, FeedByCategoryView, SecondaryNews
import json

# All tables 
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

client= Client()

dynamodb = boto3.resource('dynamodb', region_name=aws_region, aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)

class NewsTestCase(unittest.TestCase):
    '''
    Test for News model
    '''
    classes = News

    def setUp(self):
        '''
        Create a new instance of the News model before each test
        '''
        dynamodb.Table(news_table).put_item(
                Item={
                    'id': '1',
                    'title': 'test',
                    'published': '2020-10-10',
                    'description': 'test',
                    'category_id': '1',
                    'feed_id': '1',
                    'agency_id': '1',
                }
            )
        dynamodb.Table(news_table).put_item(
                Item={
                    'id': '2',
                    'title': 'test1',
                    'published': '2020-10-10',
                    'description': 'test1',
                    'category_id': '1',
                    'feed_id': '1',
                    'agency_id': '1',
                }
            )

    def test_news(self):
        '''
        Test for News model
        '''
        news1 = dynamodb.Table(news_table).get_item(Key={'id': '1'})['Item']
        news2 = dynamodb.Table(news_table).get_item(Key={'id': '2'})['Item']
        self.assertEqual(news1.title, 'test')
        self.assertEqual(news2.title, 'test1')

class CategoryTestCase(unittest.TestCase):

    def setUp(self):
        '''
        Create a new instance of the Category model before each test
        '''
        dynamodb.Table(category_table).put_item(
                Item={
                    'id': '1',
                    'name': 'test',
                }
            )
        dynamodb.Table(category_table).put_item(
                Item={
                    'id': '2',
                    'name': 'test1',
                }
            )
        
    def test_category(self):
        '''
        Test for Category model
        '''
        category1 = dynamodb.Table(category_table).get_item(Key={'id': '1'})['Item']
        category2 = dynamodb.Table(category_table).get_item(Key={'id': '2'})['Item']
        self.assertEqual(category1.name, 'test')
        self.assertEqual(category2.name, 'test1')


class TestCategory(TestCase):

    def test_category(self):
        '''
        Test for Category view
        '''
        response = client.get('/category/')
        self.assertEqual(response.status_code, 200)


class TestFeedByCategoryView(TestCase):

    def test_feed_by_category(self):
        '''
        Test for FeedByCategory view
        '''
        response = client.get('/feed/1/')
        self.assertEqual(response.status_code, 200)


class TestSecondaryNews(TestCase):

    def test_secondary_news(self):
        '''
        Test for SecondaryNews view
        '''
        response = client.get('/secondary_news/')
        self.assertEqual(response.status_code, 200)


class TestLogin(TestCase):

    def test_login(self):
        '''
        Test for Login view
        '''
        response = client.post('/login/', {'username': 'test', 'password': 'test'})
        self.assertEqual(response.status_code, 400)




