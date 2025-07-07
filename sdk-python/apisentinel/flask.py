"""
Flask middleware for API Sentinel
"""

import time
from typing import Dict, List, Any, Optional, Callable
from werkzeug.wrappers import Request, Response

from .core import SentinelCore

class SentinelMiddleware:
    """
    Flask middleware for API Sentinel
    
    This middleware captures API request/response metadata and sends it to the
    API Sentinel backend for analysis and monitoring.
    """
    
    def __init__(
        self,
        app: Callable,
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
            app: Flask WSGI application
            api_key: API Sentinel API key
            api_url: API Sentinel backend URL
            batch_size: Number of requests to batch before sending
            batch_interval: Maximum time (seconds) to wait before sending a batch
            ignore_paths: Paths to exclude from monitoring
            sensitive_headers: Headers to sanitize in logs
            sensitive_params: Query parameters to sanitize in logs
        """
        self.app = app
        self.core = SentinelCore(
            api_key=api_key,
            api_url=api_url,
            batch_size=batch_size,
            batch_interval=batch_interval,
            ignore_paths=ignore_paths,
            sensitive_headers=sensitive_headers,
            sensitive_params=sensitive_params
        )
    
    def __call__(self, environ, start_response):
        """
        WSGI middleware implementation
        
        Args:
            environ: WSGI environment
            start_response: WSGI start_response function
            
        Returns:
            WSGI response
        """
        # Create request object
        request = Request(environ)
        
        # Record start time
        start_time = time.time()
        
        # Capture response
        def capture_response(status, headers, exc_info=None):
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Parse status code
            status_code = int(status.split(" ")[0])
            
            # Get client IP
            ip = request.remote_addr
            if "X-Forwarded-For" in request.headers:
                ip = request.headers["X-Forwarded-For"].split(",")[0].strip()
            
            # Get query parameters
            query_params = {}
            for key, value in request.args.items():
                query_params[key] = value
            
            # Capture request
            self.core.capture_request(
                method=request.method,
                path=request.path,
                query_params=query_params,
                headers=dict(request.headers),
                status_code=status_code,
                latency_ms=latency_ms,
                ip=ip,
                user_agent=request.user_agent.string if request.user_agent else None
            )
            
            # Call original start_response
            return start_response(status, headers, exc_info)
        
        # Call application
        return self.app(environ, capture_response)