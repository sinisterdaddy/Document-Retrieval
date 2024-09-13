from celery import Celery

celery = Celery(__name__, broker="redis://localhost:6379/0")

@celery.task
def scrape_news():
    # Implement your scraping logic here
    pass

# Start scraping when the server starts
scrape_news.delay()
