"""
Core functionality for API Sentinel SDK
"""

import time
import threading
import json
import socket
import requests
from typing import Dict, List, Any, Optional
import logging
import geoip2.database
import os
import pkg_resources

# Configure logging
logger = logging.getLogger("apisentinel")

class SentinelCore:
    """
    Core functionality for API Sentinel SDK
    
    This class provides the core functionality for capturing API request/response
    metadata and sending it to the API Sentinel backend.
    """
    
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.apisentinel.com",
        batch_size: int = 10,
        batch_interval: int = 3,
        ignore_paths: List[str] = None,
        sensitive_headers: List[str] = None,
        sensitive_params: List[str] = None
    ):
        """
        Initialize SentinelCore
        
        Args:
            api_key: API Sentinel API key
            api_url: API Sentinel backend URL
            batch_size: Number of requests to batch before sending
            batch_interval: Maximum time (seconds) to wait before sending a batch
            ignore_paths: Paths to exclude from monitoring
            sensitive_headers: Headers to sanitize in logs
            sensitive_params: Query parameters to sanitize in logs
        """
        self.api_key = api_key
        self.api_url = api_url
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.ignore_paths = ignore_paths or []
        self.sensitive_headers = sensitive_headers or ["authorization", "cookie", "set-cookie"]
        self.sensitive_params = sensitive_params or ["password", "token", "key", "secret", "auth"]
        
        # Request queue
        self.request_queue = []
        self.queue_lock = threading.Lock()
        
        # Batch timer
        self.timer = None
        
        # GeoIP database
        self.geoip_reader = None
        try:
            geoip_path = pkg_resources.resource_filename("geoip2", "GeoLite2-Country.mmdb")
            if os.path.exists(geoip_path):
                self.geoip_reader = geoip2.database.Reader(geoip_path)
        except Exception as e:
            logger.warning(f"Failed to load GeoIP database: {e}")
    
    def capture_request(
        self,
        method: str,
        path: str,
        query_params: Dict[str, Any],
        headers: Dict[str, str],
        status_code: int,
        latency_ms: int,
        ip: str,
        user_agent: Optional[str] = None
    ):
        """
        Capture API request metadata
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            query_params: Query parameters
            headers: Request headers
            status_code: Response status code
            latency_ms: Request latency in milliseconds
            ip: Client IP address
            user_agent: User-Agent string
        """
        # Skip ignored paths
        if any(path.startswith(ignore_path) for ignore_path in self.ignore_paths):
            return
        
        # Sanitize headers
        sanitized_headers = self._sanitize_headers(headers)
        
        # Sanitize query parameters
        sanitized_params = self._sanitize_query_params(query_params)
        
        # Get country code from IP
        country_code = self._get_country_code(ip)
        
        # Create request log
        request_log = {
            "method": method,
            "path": path,
            "query_params": sanitized_params,
            "headers": sanitized_headers,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "ip": ip,
            "user_agent": user_agent,
            "country_code": country_code
        }
        
        # Add to queue
        with self.queue_lock:
            self.request_queue.append(request_log)
            
            # Send batch if queue is full
            if len(self.request_queue) >= self.batch_size:
                self._send_batch()
            else:
                self._start_timer()
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers by redacting sensitive values
        
        Args:
            headers: Request headers
            
        Returns:
            Sanitized headers
        """
        sanitized = {}
        
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _sanitize_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize query parameters by redacting sensitive values
        
        Args:
            params: Query parameters
            
        Returns:
            Sanitized query parameters
        """
        sanitized = {}
        
        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_params):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _get_country_code(self, ip: str) -> Optional[str]:
        """
        Get country code from IP address
        
        Args:
            ip: IP address
            
        Returns:
            Country code (ISO 3166-1 alpha-2) or None
        """
        if not ip or ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):
            return None
        
        try:
            if self.geoip_reader:
                response = self.geoip_reader.country(ip)
                return response.country.iso_code
        except Exception:
            pass
        
        return None
    
    def _start_timer(self):
        """Start batch timer"""
        if self.timer:
            self.timer.cancel()
        
        self.timer = threading.Timer(self.batch_interval, self._send_batch)
        self.timer.daemon = True
        self.timer.start()
    
    def _send_batch(self):
        """Send batched requests to API Sentinel"""
        with self.queue_lock:
            if not self.request_queue:
                return
            
            batch = self.request_queue.copy()
            self.request_queue = []
        
        try:
            response = requests.post(
                f"{self.api_url}/api/ingest",
                json={"requests": batch},
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=5
            )
            
            if response.status_code != 201:
                logger.error(f"API Sentinel: Error sending batch: {response.status_code} {response.text}")
                
                # Add requests back to queue if sending fails
                with self.queue_lock:
                    self.request_queue = batch + self.request_queue
        
        except Exception as e:
            logger.error(f"API Sentinel: Error sending batch: {str(e)}")
            
            # Add requests back to queue if sending fails
            with self.queue_lock:
                self.request_queue = batch + self.request_queue