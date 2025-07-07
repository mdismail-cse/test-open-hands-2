from jobs.celery_app import celery_app
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta

from core.database import SessionLocal
from core.anomaly_detector import AnomalyDetector
from core.doc_generator import OpenAPIGenerator
from core.alert_system import AlertSystem
from core.models import Project, Anomaly

@celery_app.task
def detect_anomalies(project_id: str):
    """
    Background task to detect anomalies for a project
    
    This task runs the anomaly detection algorithms and creates
    anomaly records in the database.
    """
    db = SessionLocal()
    try:
        # Convert string to UUID
        project_uuid = uuid.UUID(project_id)
        
        # Create anomaly detector
        detector = AnomalyDetector(db, project_uuid)
        
        # Detect anomalies
        anomalies = detector.detect_anomalies()
        
        # Return number of anomalies detected
        return len(anomalies)
    finally:
        db.close()

@celery_app.task
def generate_api_docs(project_id: str):
    """
    Background task to generate API documentation for a project
    
    This task analyzes API request logs and generates OpenAPI
    documentation using GPT.
    """
    db = SessionLocal()
    try:
        # Convert string to UUID
        project_uuid = uuid.UUID(project_id)
        
        # Create OpenAPI generator
        generator = OpenAPIGenerator(db, project_uuid)
        
        # Generate OpenAPI spec
        api_doc = generator.generate_openapi_spec()
        
        # Return success status
        return api_doc is not None
    finally:
        db.close()

@celery_app.task
async def send_anomaly_alert(anomaly_id: str):
    """
    Background task to send alerts for an anomaly
    
    This task sends alerts via configured channels (email, Slack, webhook)
    for a specific anomaly.
    """
    db = SessionLocal()
    try:
        # Create alert system
        alert_system = AlertSystem(db)
        
        # Send alert
        success = await alert_system.send_alert(anomaly_id)
        
        # Return success status
        return success
    finally:
        db.close()

@celery_app.task
def schedule_anomaly_detection():
    """
    Scheduled task to run anomaly detection for all projects
    
    This task is scheduled to run periodically and triggers
    anomaly detection for all active projects.
    """
    db = SessionLocal()
    try:
        # Get all projects
        projects = db.query(Project).all()
        
        # Schedule anomaly detection for each project
        for project in projects:
            detect_anomalies.delay(str(project.id))
        
        # Return number of projects processed
        return len(projects)
    finally:
        db.close()

@celery_app.task
def schedule_api_doc_generation():
    """
    Scheduled task to run API documentation generation for all projects
    
    This task is scheduled to run periodically and triggers
    API documentation generation for all active projects.
    """
    db = SessionLocal()
    try:
        # Get all projects
        projects = db.query(Project).all()
        
        # Schedule API doc generation for each project
        for project in projects:
            generate_api_docs.delay(str(project.id))
        
        # Return number of projects processed
        return len(projects)
    finally:
        db.close()

@celery_app.task
async def process_new_anomalies():
    """
    Scheduled task to process and send alerts for new anomalies
    
    This task is scheduled to run periodically and sends alerts
    for new anomalies that haven't been processed yet.
    """
    db = SessionLocal()
    try:
        # Get recent unprocessed anomalies (last hour)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        anomalies = db.query(Anomaly).filter(
            Anomaly.created_at >= recent_time,
            Anomaly.processed == False
        ).all()
        
        # Send alerts for each anomaly
        for anomaly in anomalies:
            # Mark as processed
            anomaly.processed = True
            db.commit()
            
            # Send alert
            await send_anomaly_alert.delay(str(anomaly.id))
        
        # Return number of anomalies processed
        return len(anomalies)
    finally:
        db.close()