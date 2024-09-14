from celery import Celery
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, exceptions as es_exceptions

# Initialize Celery
celery = Celery(__name__, broker="redis://localhost:6379/0")

# Initialize Elasticsearch client
try:
    es = Elasticsearch(hosts=["http://localhost:9200"])
    es.info()  # Test the connection to Elasticsearch
except es_exceptions.ConnectionError as e:
    print(f"Elasticsearch connection error: {e}")
    es = None

@celery.task
def scrape_news():
    url = "https://news.ycombinator.com/"  # Example news site (Hacker News)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the news: {e}")
        return

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

    if es:
        # Store in Elasticsearch
        for article in articles:
            try:
                es.index(index="news", body=article)
            except es_exceptions.ElasticsearchException as e:
                print(f"Error indexing article: {e}")

        print(f"Scraped and indexed {len(articles)} articles.")
    else:
        print("Elasticsearch client not initialized; skipping indexing.")

# You might want to remove this to avoid immediate task execution on module load
# scrape_news.delay()
