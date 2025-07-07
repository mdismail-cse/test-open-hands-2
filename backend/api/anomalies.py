from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from core.database import get_db
from core.schemas import AnomalyResponse
from core.models import Anomaly, Project, User
from core.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AnomalyResponse])
async def get_anomalies(
    project_id: Optional[uuid.UUID] = None,
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get anomalies
    
    Returns anomalies for the authenticated user's projects.
    """
    # Build query
    query = db.query(Anomaly).join(Project).filter(Project.user_id == current_user.id)
    
    # Apply filters
    if project_id:
        query = query.filter(Anomaly.project_id == project_id)
    
    if resolved is not None:
        query = query.filter(Anomaly.resolved == resolved)
    
    # Apply pagination
    query = query.order_by(Anomaly.created_at.desc()).offset(offset).limit(limit)
    
    # Execute query
    anomalies = query.all()
    
    return anomalies

@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly(
    anomaly_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get anomaly by ID
    
    Returns a specific anomaly for the authenticated user.
    """
    # Get anomaly
    anomaly = db.query(Anomaly).join(Project).filter(
        Anomaly.id == anomaly_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if anomaly exists
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomaly not found"
        )
    
    return anomaly

@router.post("/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(
    anomaly_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resolve anomaly
    
    Marks a specific anomaly as resolved.
    """
    # Get anomaly
    anomaly = db.query(Anomaly).join(Project).filter(
        Anomaly.id == anomaly_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if anomaly exists
    if not anomaly:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anomaly not found"
        )
    
    # Mark as resolved
    anomaly.resolved = True
    anomaly.resolved_at = datetime.utcnow()
    
    # Commit changes
    db.commit()
    db.refresh(anomaly)
    
    return anomaly