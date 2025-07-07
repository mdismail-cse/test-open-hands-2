from pydantic import BaseModel, Field, EmailStr, validator, UUID4
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID4
    api_key: str
    user_id: UUID4
    created_at: datetime
    request_count: int
    
    class Config:
        from_attributes = True

# API Request schemas
class ApiRequestBase(BaseModel):
    method: str
    path: str
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    status_code: int
    latency_ms: int
    ip: str
    user_agent: Optional[str] = None
    country_code: Optional[str] = None

class ApiRequestCreate(ApiRequestBase):
    pass

class ApiRequestBatch(BaseModel):
    requests: List[ApiRequestCreate]

class ApiRequestResponse(ApiRequestBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    
    class Config:
        from_attributes = True

# Anomaly schemas
class AnomalyType(str, Enum):
    NEW_ENDPOINT = "new_endpoint"
    RATE_LIMIT = "rate_limit"
    ERROR_SPIKE = "error_spike"
    SUSPICIOUS_LOCATION = "suspicious_location"
    UNUSUAL_PATTERN = "unusual_pattern"

class AnomalySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnomalyBase(BaseModel):
    type: AnomalyType
    endpoint_path: Optional[str] = None
    ip: Optional[str] = None
    message: str
    severity: AnomalySeverity

class AnomalyCreate(AnomalyBase):
    project_id: UUID4

class AnomalyResponse(AnomalyBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# API Documentation schemas
class ApiDocBase(BaseModel):
    json_content: Dict[str, Any]

class ApiDocCreate(ApiDocBase):
    project_id: UUID4

class ApiDocResponse(ApiDocBase):
    id: UUID4
    project_id: UUID4
    generated_at: datetime
    
    class Config:
        from_attributes = True

# Alert Channel schemas
class AlertChannelType(str, Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

class AlertChannelBase(BaseModel):
    type: AlertChannelType
    config: Dict[str, Any]
    active: bool = True

class AlertChannelCreate(AlertChannelBase):
    project_id: UUID4

class AlertChannelResponse(AlertChannelBase):
    id: UUID4
    project_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None