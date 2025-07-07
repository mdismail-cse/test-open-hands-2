from celery import Celery
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Redis URL from environment variable
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "api_sentinel",
    broker=redis_url,
    backend=redis_url,
    include=["jobs.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1
)

if __name__ == "__main__":
    celery_app.start()