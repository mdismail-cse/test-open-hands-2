from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from core.database import get_db
from core.schemas import ApiRequestBatch
from core.models import ApiRequest, Project
from core.auth import get_project_from_api_key

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def ingest_api_requests(
    request_batch: ApiRequestBatch,
    project: Project = Depends(get_project_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Ingest a batch of API requests
    
    This endpoint receives batched API request logs from the SDK middleware
    and stores them in the database.
    """
    # Create API request records
    api_requests = []
    for request_data in request_batch.requests:
        api_request = ApiRequest(
            id=uuid.uuid4(),
            project_id=project.id,
            method=request_data.method,
            path=request_data.path,
            headers=request_data.headers,
            query_params=request_data.query_params,
            status_code=request_data.status_code,
            latency_ms=request_data.latency_ms,
            ip=request_data.ip,
            user_agent=request_data.user_agent,
            country_code=request_data.country_code
        )
        api_requests.append(api_request)
    
    # Add all requests to the database
    db.add_all(api_requests)
    
    # Update project request count
    project.request_count += len(api_requests)
    
    # Commit changes
    db.commit()
    
    # Trigger anomaly detection (async)
    # This would typically be done via a background task or message queue
    # For now, we'll just return a success response
    
    return {"status": "success", "message": f"Ingested {len(api_requests)} API requests"}