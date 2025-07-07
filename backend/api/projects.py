from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from core.database import get_db
from core.schemas import ProjectCreate, ProjectResponse
from core.models import Project, User
from core.auth import get_current_user, generate_api_key

router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project
    
    Creates a new project for the authenticated user.
    """
    # Generate API key
    api_key = generate_api_key()
    
    # Create project
    db_project = Project(
        id=uuid.uuid4(),
        name=project.name,
        description=project.description,
        api_key=api_key,
        user_id=current_user.id
    )
    
    # Add project to database
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects
    
    Returns all projects for the authenticated user.
    """
    # Get projects for current user
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get project by ID
    
    Returns a specific project for the authenticated user.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if project exists
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update project
    
    Updates a specific project for the authenticated user.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if project exists
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update project
    project.name = project_data.name
    project.description = project_data.description
    
    # Commit changes
    db.commit()
    db.refresh(project)
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project
    
    Deletes a specific project for the authenticated user.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if project exists
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete project
    db.delete(project)
    db.commit()
    
    return None

@router.post("/{project_id}/regenerate-key", response_model=ProjectResponse)
async def regenerate_api_key(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate API key
    
    Regenerates the API key for a specific project.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    # Check if project exists
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Generate new API key
    project.api_key = generate_api_key()
    
    # Commit changes
    db.commit()
    db.refresh(project)
    
    return project