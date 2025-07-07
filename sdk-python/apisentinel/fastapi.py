"""
FastAPI middleware for API Sentinel
"""

import time
from typing import Dict, List, Any, Optional, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .core import SentinelCore

class SentinelMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for API Sentinel
    
    This middleware captures API request/response metadata and sends it to the
    API Sentinel backend for analysis and monitoring.
    """
    
    def __init__(
        self,
        app,
        api_key: str,
        api_url: str = "https://api.apisentinel.com",
        batch_size: int = 10,
        batch_interval: int = 3,
        ignore_paths: List[str] = None,
        sensitive_headers: List[str] = None,
        sensitive_params: List[str] = None
    ):
        """
        Initialize SentinelMiddleware
        
        Args:
            app: FastAPI application
            api_key: API Sentinel API key
            api_url: API Sentinel backend URL
            batch_size: Number of requests to batch before sending
            batch_interval: Maximum time (seconds) to wait before sending a batch
            ignore_paths: Paths to exclude from monitoring
            sensitive_headers: Headers to sanitize in logs
            sensitive_params: Query parameters to sanitize in logs
        """
        super().__init__(app)
        self.core = SentinelCore(
            api_key=api_key,
            api_url=api_url,
            batch_size=batch_size,
            batch_interval=batch_interval,
            ignore_paths=ignore_paths,
            sensitive_headers=sensitive_headers,
            sensitive_params=sensitive_params
        )
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and response
        
        Args:
            request: Starlette Request
            call_next: Next middleware or route handler
            
        Returns:
            Starlette Response
        """
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Get client IP
        ip = self._get_client_ip(request)
        
        # Get query parameters
        query_params = {}
        for key, value in request.query_params.items():
            query_params[key] = value
        
        # Capture request
        self.core.capture_request(
            method=request.method,
            path=request.url.path,
            query_params=query_params,
            headers=dict(request.headers),
            status_code=response.status_code,
            latency_ms=latency_ms,
            ip=ip,
            user_agent=request.headers.get("user-agent")
        )
        
        return response
    
    def _get_client_ip(self, request: Request):
        """
        Get client IP address from request
        
        Args:
            request: Starlette Request
            
        Returns:
            Client IP address
        """
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        
        client = request.scope.get("client")
        if client:
            return client[0]
        
        return None