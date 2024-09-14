from celery import Celery
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

# Initialize Celery
celery = Celery(__name__, broker="redis://localhost:6379/0")

# Initialize Elasticsearch client
es = Elasticsearch()

@celery.task
def scrape_news():
    url = "https://news.ycombinator.com/"  # Example news site (Hacker News)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    # Example of scraping headlines
    for item in soup.find_all('a', class_='storylink'):
        title = item.get_text()
        link = item.get('href')
        articles.append({
            "title": title,
            "link": link,
            "content": title  # Here you can add more content if available
        })

    # Store in Elasticsearch
    for article in articles:
        es.index(index="news", body=article)

    print(f"Scraped and indexed {len(articles)} articles.")

# Start scraping when the server starts
scrape_news.delay()
