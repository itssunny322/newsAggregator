import feedparser
import time
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

# AWS credentials and region configuration
aws_access_key_id = 'AKIAV7H3MVMN6W4KCRGR'
aws_secret_access_key = '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'
aws_region = 'ap-south-1'

# Define the SQS queue
sqs = boto3.client('sqs', region_name=aws_region)
queue_url = 'https://sqs.ap-south-1.amazonaws.com/410696592155/groupFeed'

# DynamoDB table configuration
news_group = 'news_group'
secondary_news = 'secondary_news'
news_table = 'News'

# DynamoDB table configuration
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1', aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)

# Jaccard similarity
def jaccard_similarity(str1, str2):
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())
    
    if len(set1) == 0 and len(set2) == 0:
        return 1.0  # Both sets are empty, consider them as similar
    
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    similarity = len(intersection) / len(union)
    return similarity

# Check if two strings are similar
def is_similar(article1, article2, threshold):
    similarity = jaccard_similarity(article1, article2)
    return similarity >= threshold

# Fetch data from sqs queue
def fetch_data():
    while True:
        # Receive messages from SQS queue
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,  # Maximum number of messages to retrieve (adjust as needed)
            WaitTimeSeconds=3  # Wait time in seconds for receiving messages (adjust as needed)
        )

        # Check if the queue is empty
        if 'Messages' in response:
            for message in response['Messages']:
                # Extract the message body and save it to news
                news = eval(message['Body'])

                # check if news is similar to any news in the news table

                # Retrieve all the news articles from the same category and not from the same agency
                news_articles = dynamodb.Table(news_table).scan(
                    FilterExpression=Attr('category_id').eq(news['category_id']) & Attr('agency_id').ne(
                        news['agency_id'])
                )['Items']


                # Compare the entry with all the news articles
                for article in news_articles:

                    # Check if the entry is similar to the article
                    if news['description'] != '' and article['description'] != '':
                        if is_similar(news['description'], article['description'], 0.5) or is_similar(news['title'], article['title'], 0.5):

                            hashObj = hashlib.md5(news['url'].encode()).hexdigest()
                            primary_news_id = hashObj.hexdigest()
                            # Save to the news group table
                            dynamodb.Table(news_group).put_item(
                                Item={
                                    'id': primary_news_id,
                                    'primary_news_id': news['id'],
                                    'secondary_news_id': []
                                }
                            )
                            
                            hashObj = hashlib.md5(article['url'].encode()).hexdigest()
                            secondary_news_id = hashObj.hexdigest()
                            # Save to the secondary news table
                            dynamodb.Table(secondary_news).put_item(
                                Item={
                                    'id': secondary_news_id,
                                    'news_group_id': news['id'],
                                    'news_item_id': primary_news_id
                                }
                            )

                            # Update the news group table
                            dynamodb.Table(news_group).update_item(
                                Key={
                                    'id': news['id']
                                },
                                UpdateExpression="SET secondary_news_id = list_append(secondary_news_id, :i)",
                                ExpressionAttributeValues={
                                    ':i': [secondary_news_id]
                                }
                            )

                # Delete that particular message from the queue
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

        else:
            print('Queue is empty')
            break

fetch_data()