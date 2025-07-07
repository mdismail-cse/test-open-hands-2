"""
Django middleware for API Sentinel
"""

import time
from typing import Dict, List, Any, Optional, Callable
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .core import SentinelCore

class SentinelMiddleware:
    """
    Django middleware for API Sentinel
    
    This middleware captures API request/response metadata and sends it to the
    API Sentinel backend for analysis and monitoring.
    """
    
    def __init__(self, get_response):
        """
        Initialize SentinelMiddleware
        
        Args:
            get_response: Django get_response function
        """
        self.get_response = get_response
        
        # Get settings from Django settings
        sentinel_settings = getattr(settings, "API_SENTINEL", {})
        
        api_key = sentinel_settings.get("api_key")
        if not api_key:
            raise ValueError("API Sentinel: API key is required in settings.API_SENTINEL")
        
        # Initialize core
        self.core = SentinelCore(
            api_key=api_key,
            api_url=sentinel_settings.get("api_url", "https://api.apisentinel.com"),
            batch_size=sentinel_settings.get("batch_size", 10),
            batch_interval=sentinel_settings.get("batch_interval", 3),
            ignore_paths=sentinel_settings.get("ignore_paths", []),
            sensitive_headers=sentinel_settings.get("sensitive_headers", ["authorization", "cookie", "set-cookie"]),
            sensitive_params=sentinel_settings.get("sensitive_params", ["password", "token", "key", "secret", "auth"])
        )
    
    def __call__(self, request):
        """
        Process request and response
        
        Args:
            request: Django HttpRequest
            
        Returns:
            Django HttpResponse
        """
        # Record start time
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Get client IP
        ip = self._get_client_ip(request)
        
        # Get query parameters
        query_params = {}
        for key, value in request.GET.items():
            query_params[key] = value
        
        # Capture request
        self.core.capture_request(
            method=request.method,
            path=request.path,
            query_params=query_params,
            headers=dict(request.headers),
            status_code=response.status_code,
            latency_ms=latency_ms,
            ip=ip,
            user_agent=request.headers.get("User-Agent")
        )
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get client IP address from request
        
        Args:
            request: Django HttpRequest
            
        Returns:
            Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip