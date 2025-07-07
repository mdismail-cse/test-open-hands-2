from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models
from backend.core.models import Base
from backend.core.auth import get_password_hash, generate_api_key
from backend.core.models import User, Project
import uuid

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

def create_tables():
    """Create database tables"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database tables created successfully")

def create_admin_user():
    """Create admin user"""
    from sqlalchemy.orm import sessionmaker
    
    # Create session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_email = os.getenv("ADMIN_EMAIL", "admin@apisentinel.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        admin = db.query(User).filter(User.email == admin_email).first()
        if admin:
            print(f"Admin user {admin_email} already exists")
            return
        
        # Create admin user
        admin = User(
            id=uuid.uuid4(),
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name="API Sentinel Admin"
        )
        
        # Add admin user to database
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # Create demo project
        demo_project = Project(
            id=uuid.uuid4(),
            name="Demo Project",
            description="A demo project for API Sentinel",
            api_key=generate_api_key(),
            user_id=admin.id
        )
        
        # Add demo project to database
        db.add(demo_project)
        db.commit()
        
        print(f"Admin user {admin_email} created successfully")
        print(f"Demo project created with API key: {demo_project.api_key}")
    
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    create_admin_user()