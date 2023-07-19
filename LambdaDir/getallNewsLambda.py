import json
import boto3
from boto3.dynamodb.conditions import Key, Attr


# DynamoDB table configuration
news_table = 'News'
aws_region = 'ap-south-1'

# DynamoDB table configuration
dynamodb = boto3.resource('dynamodb', region_name=aws_region)

def lambda_handler(event, context):
    # TODO implement
    news = dynamodb.Table(news_table).scan()['Items']

    return {
        'statusCode': 200,
        'body': json.dumps(news)
    }
