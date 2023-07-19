# NewsAggregator

## Description

This is a news aggregator that collects news periodically every hour from different sources and displays them in a single page. The news are collected from the following sources:

- [The Times of India](https://timesofindia.indiatimes.com/rss.cms)
- [Hindustan Times](https://www.hindustantimes.com/rss/)
- [The Hindu](https://www.thehindu.com/rssfeeds/)

## Installation

1. Clone the repository
2. Navigate to the project directory
3. Run the docker command "docker-compose build"
4. Run the command "docker-compose up"
5. Open the link " http://127.0.0.1:8000/" to check if its running

## Tools Used

- Django
- Django Rest Framework
- Docker
- AWS EventBridge, Lambda, SQS, DLQ, IAM, ECR, ECS
- Swagger

## API Documentation

API documentation can be found at "https://app.swaggerhub.com/apis/MFSISUNNYS/NewsAggregator/1.0.0"
