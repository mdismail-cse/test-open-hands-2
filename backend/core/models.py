from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    api_key = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    request_count = Column(Integer, default=0)
    
class ApiRequest(Base):
    __tablename__ = "api_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    headers = Column(JSONB)
    query_params = Column(JSONB)
    status_code = Column(Integer)
    latency_ms = Column(Integer)
    ip = Column(INET)
    user_agent = Column(Text)
    country_code = Column(String(2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnomalyType(str, enum.Enum):
    NEW_ENDPOINT = "new_endpoint"
    RATE_LIMIT = "rate_limit"
    ERROR_SPIKE = "error_spike"
    SUSPICIOUS_LOCATION = "suspicious_location"
    UNUSUAL_PATTERN = "unusual_pattern"

class AnomalySeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    type = Column(Enum(AnomalyType), nullable=False)
    endpoint_path = Column(String)
    ip = Column(INET)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AnomalySeverity), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    processed = Column(Boolean, default=False)

class ApiDoc(Base):
    __tablename__ = "api_docs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    json_content = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

class AlertChannel(Base):
    __tablename__ = "alert_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    type = Column(String, nullable=False)  # email, slack, webhook
    config = Column(JSONB, nullable=False)  # email address, webhook URL, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)