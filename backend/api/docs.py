from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from core.database import get_db
from core.schemas import ApiDocResponse
from core.models import ApiDoc, Project, User
from core.auth import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}", response_model=ApiDocResponse)
async def get_api_docs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get API documentation
    
    Returns the latest API documentation for a specific project.
    """
    # Check if project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get latest API documentation
    api_doc = db.query(ApiDoc).filter(
        ApiDoc.project_id == project_id
    ).order_by(ApiDoc.generated_at.desc()).first()
    
    if not api_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API documentation not found"
        )
    
    return api_doc

@router.post("/projects/{project_id}/generate", response_model=ApiDocResponse)
async def generate_api_docs(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate API documentation
    
    Triggers the generation of API documentation for a specific project.
    This is an asynchronous operation and will return the latest documentation.
    """
    # Check if project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get latest API documentation
    api_doc = db.query(ApiDoc).filter(
        ApiDoc.project_id == project_id
    ).order_by(ApiDoc.generated_at.desc()).first()
    
    if not api_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API documentation not found or not yet generated"
        )
    
    # In a real implementation, we would trigger a background job to generate
    # new documentation. For now, we'll just return the latest documentation.
    
    return api_doc