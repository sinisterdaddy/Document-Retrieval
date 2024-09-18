<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body>

<h1>Document Retrieval System</h1>

<h2>Overview</h2>
<p>This project is a backend document retrieval system designed for chat applications to use as context. The system scrapes news articles, stores them in an Elasticsearch database, and provides fast retrieval via an API. The backend is built with FastAPI, and the system utilizes Redis for caching and Elasticsearch for document storage.</p> 

<h2>Features</h2>
<ul>
    <li><strong>Document Storage:</strong> Scraped documents are stored in Elasticsearch.</li>
    <li><strong>Caching:</strong> Layered caching with Redis and an LRU cache for improved retrieval speed.</li>
    <li><strong>Background Scraping:</strong> Automatically scrapes news articles when the server starts.</li>
    <li><strong>Rate Limiting:</strong> Limits user requests to prevent abuse.</li>
    <li><strong>Dockerized:</strong> The entire application is containerized for easy deployment.</li>
</ul>

<h2>Requirements</h2>
<ul>
    <li>Python 3.9+</li>
    <li>Docker (for containerization)</li>
    <li>Redis (for caching)</li>
    <li>Elasticsearch (for document storage)</li>
</ul>

<h2>Project Structure</h2>
<pre>
.
├── app
│   ├── api
│   │   └── routes.py      # API routes
│   ├── main.py            # FastAPI application entry point
│   ├── tasks.py           # Celery tasks for background jobs
│   ├── models.py          # Data models and Redis interaction
│   ├── caching.py         # Caching implementations
├── Dockerfile             # Dockerfile for building the image
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
</pre>

<h2>Setup</h2>

<h3>1. Clone the Repository</h3>
<pre>
git clone https://github.com/yourusername/document-retrieval.git
cd document-retrieval
</pre>

<h3>2. Environment Setup</h3>

<h4>Using Docker</h4>
<p>The easiest way to set up the environment is by using Docker.</p>

<p><strong>Docker Compose:</strong></p>
<p>Create a <code>docker-compose.yml</code> file:</p>
<pre>
version: '3'
services:
  redis:
    image: "redis:latest"
    container_name: redis
    ports:
      - "6379:6379"

  elasticsearch:
    image: "elasticsearch:7.10.0"
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  app:
    build: .
    container_name: docretrieval-app
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - elasticsearch
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
</pre>

<p>Then, run:</p>
<pre>docker-compose up --build</pre>

<p>This will build and run all necessary services (FastAPI app, Redis, and Elasticsearch).</p>

<h4>Without Docker</h4>
<ol>
    <li><strong>Install Dependencies:</strong>
    <pre>pip install -r requirements.txt</pre></li>

    <li><strong>Run Redis:</strong>
    <p>Ensure Redis is running locally:</p>
    <pre>redis-server</pre></li>

    <li><strong>Run Elasticsearch:</strong>
    <p>Ensure Elasticsearch is running locally:</p>
    <pre>docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.10.0</pre></li>

    <li><strong>Start FastAPI Server:</strong>
    <pre>uvicorn app.main:app --host 0.0.0.0 --port 8000</pre></li>
</ol>

<h2>API Endpoints</h2>

<h3>1. Health Check</h3>
<ul>
    <li><strong>Endpoint:</strong> <code>/health</code></li>
    <li><strong>Method:</strong> <code>GET</code></li>
    <li><strong>Description:</strong> Checks if the API is running.</li>
</ul>
<p><strong>Example:</strong></p>
<pre>curl -X GET "http://localhost:8000/health"</pre>

<h3>2. Search Documents</h3>
<ul>
    <li><strong>Endpoint:</strong> <code>/search</code></li>
    <li><strong>Method:</strong> <code>GET</code></li>
    <li><strong>Description:</strong> Retrieves a list of documents based on a search query.</li>
    <li><strong>Parameters:</strong>
        <ul>
            <li><code>text</code> (string): The search query text.</li>
            <li><code>user_id</code> (string): The ID of the user making the request.</li>
            <li><code>top_k</code> (int, default=10): The number of top results to return.</li>
            <li><code>threshold</code> (float, default=0.5): The minimum similarity score threshold.</li>
        </ul>
    </li>
</ul>
<p><strong>Example:</strong></p>
<pre>curl -X GET "http://localhost:8000/search?text=document&user_id=123&top_k=10&threshold=0.5"</pre>

<h3>3. Rate Limiting</h3>
<p><strong>Description:</strong> Users are limited to 5 requests within a specified period. Exceeding this limit results in an HTTP 429 status code.</p>

<h2>Caching Strategy</h2>

<h3>1. Redis</h3>
<p>Redis is used as the primary caching mechanism to store the results of search queries for faster retrieval. Redis offers persistence and scalability, making it an ideal choice for this system.</p>

<h3>2. LRU Cache</h3>
<p>An in-memory LRU (Least Recently Used) cache is implemented for even faster access to frequently requested data. This cache is layered on top of Redis to provide a multi-tier caching strategy.</p>

<p><strong>Reasoning:</strong></p>
<ul>
    <li><strong>Performance:</strong> Redis provides fast read/write operations, while the LRU cache reduces the load on Redis by keeping frequently accessed data in-memory.</li>
    <li><strong>Scalability:</strong> Redis can be scaled horizontally, allowing the system to handle increased load.</li>
    <li><strong>Persistence:</strong> Redis ensures that cached data is not lost between restarts.</li>
</ul>

<h2>Background Scraping</h2>
<p>The system uses Celery for background scraping tasks. When the server starts, a Celery worker is initiated that scrapes news articles and stores them in Elasticsearch.</p>

<p><strong>Command:</strong></p>
<p>To start the Celery worker:</p>
<pre>celery -A app.tasks worker --loglevel=info</pre>

<h2>Error Handling & Logging</h2>
<p>The system is equipped with global error handling to catch exceptions and log them for debugging purposes. The logs can be found in the application logs or the Docker container logs.</p>

<h2>Testing</h2>

<h3>Manual Testing</h3>
<p>You can test the API endpoints using tools like Curl, Postman, or Thunder Client (in VS Code).</p>

<h3>Automated Testing</h3>
<p>To be implemented: The project can include unit tests using <code>pytest</code> for automated testing of various components.</p>

<h2>Deployment</h2>
<p>The system can be deployed using Docker, making it platform-independent. Ensure that the necessary services (Redis, Elasticsearch) are also deployed in the same environment.</p>

<h2>Future Enhancements</h2>
<ul>
    <li><strong>Re-ranking Algorithms:</strong> Implement re-ranking of search results based on relevance and user preferences.</li>
    <li><strong>Fine-tuning:</strong> Add scripts for fine-tuning the retriever models to improve the accuracy of search results.</li>
    <li><strong>User Authentication:</strong> Integrate user authentication and authorization mechanisms.</li>
</ul>

<h2>Contributing</h2>
<p>Contributions are welcome! Please fork this repository and create a pull request with your changes.</p>

<h2>License</h2>
<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>

</body>
</html>
