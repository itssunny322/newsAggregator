import feedparser
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import uuid
import hashlib
from decouple import config

# AWS credentials and region configuration
aws_access_key_id = config('AWS_ACCESS_KEY_ID')
aws_secret_access_key = config('AWS_SECRET_ACCESS_KEY')
aws_region = config('AWS_REGION')

# DynamoDB table configuration
news_table = 'News'
category_table = 'Category'
agency_table = 'Agency'
feed_table = 'Feed'

    
# Create a DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

# Define the SQS queue
sqs = boto3.client('sqs', region_name=aws_region)
queue_url = 'https://sqs.ap-south-1.amazonaws.com/410696592155/groupFeed'


def fetch_news(rss_url, category, agency):
    
    try :
        # Parse the RSS feed
        feed = feedparser.parse(rss_url)

        # Iterate over each entry in the feed
        for entry in feed.entries:
            # Extract relevant information from the entry
            title = entry.title
            link = entry.link
            published = entry.published
            description = entry.summary

            # Retrieve category ID from DynamoDB
            category_id = dynamodb.Table(category_table).scan(
                FilterExpression=Key('name').eq(category)
            )['Items'][0]['id']

            # Retrieve agency ID from DynamoDB
            agency_id = dynamodb.Table(agency_table).scan(
                FilterExpression=Key('name').eq(agency)
            )['Items'][0]['id']

            # Retrieve feed ID from DynamoDB
            feed_id = dynamodb.Table(feed_table).scan(
                FilterExpression=Key('url').eq(rss_url)
            )['Items'][0]['id']
            
            # Create a unique uuid for the entry
            hashObj = hashlib.md5(link.encode())
            id = hashObj.hexdigest()

            # Check if the entry already exists in the DynamoDB table

            if len(dynamodb.Table(news_table).scan(
                FilterExpression=Key('id').eq(id)
            )['Items']) < 1:
                # Put the entry into the DynamoDB table
                dynamodb.Table(news_table).put_item(
                    Item={
                        'id': id,
                        'title': title,
                        'link': link,
                        'published': published,
                        'description': description,
                        'category_id': category_id,
                        'feed_id': feed_id,
                    }
                )

                # Send the entry to the SQS queue
                sqs.send_message(
                            QueueUrl=queue_url,
                            MessageBody=json.dumps(
                                {
                                    'id': id,
                                    'title': title,
                                    'link': link,
                                    'published': published,
                                    'description': description,
                                    'category_id': category_id,
                                    'feed_id': feed_id,
                                    'agency_id': agency_id
                                }
                            )
                        )

            else:
                print("News already exists in the database")
    
    except Exception as e:
        print(e)
        print("Error fetching news from " + agency + " for " + category)

# category include india, world, business, sports, technology, entertainment, science, health
# categories = ["india", "world", "business", "sports", "technology", "entertainment", "science", "health"]
categories = ["india", "sports"]
feeds = {
        "india": {
            "thehindu": "https://www.thehindu.com/news/national/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml"
        },
        "world" : {
            "thehindu": "https://www.thehindu.com/news/international/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/world/rssfeed.xml"
        },
        "business" : {
            "thehindu": "https://www.thehindu.com/business/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml"
        },
        "sports" : {
            "thehindu": "https://www.thehindu.com/sport/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/sports/rssfeed.xml"
        },
        "technology" : {
            "thehindu": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/tech/rssfeed.xml"
        },
        "entertainment" : {
            "thehindu": "https://www.thehindu.com/entertainment/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/entertainment/rssfeed.xml"
        },
        "science" : {
            "thehindu": "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/science/rssfeed.xml"
        },
        "health" : {
            "thehindu": "https://www.thehindu.com/sci-tech/health/feeder/default.rss",
            "timesofindia": "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",
            "hindustantimes": "https://www.hindustantimes.com/feeds/rss/health/rssfeed.xml"
        }
    }

# Fetch news for each category

for category in categories:
        if category in feeds:
            feed_urls = feeds[category]
            for agency, rss_url in feed_urls.items():
                fetch_news(rss_url, category, agency)
                # print(rss_url, category, agency)
        else:
            print("Category not found")



