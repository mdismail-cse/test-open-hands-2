from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta
import uuid
import ipaddress

from core.models import ApiRequest, Anomaly, AnomalyType, AnomalySeverity, Project

class AnomalyDetector:
    def __init__(self, db: Session, project_id: uuid.UUID):
        self.db = db
        self.project_id = project_id
        self.suspicious_countries = ["KP", "IR", "SY", "CU"]  # Example list
    
    def detect_anomalies(self):
        """
        Detect anomalies in API requests
        
        This method runs various detection algorithms to identify potential
        security anomalies in the API traffic.
        """
        anomalies = []
        
        # Detect new endpoints
        new_endpoint_anomalies = self._detect_new_endpoints()
        anomalies.extend(new_endpoint_anomalies)
        
        # Detect rate limit violations
        rate_limit_anomalies = self._detect_rate_limit_violations()
        anomalies.extend(rate_limit_anomalies)
        
        # Detect error spikes
        error_spike_anomalies = self._detect_error_spikes()
        anomalies.extend(error_spike_anomalies)
        
        # Detect suspicious locations
        suspicious_location_anomalies = self._detect_suspicious_locations()
        anomalies.extend(suspicious_location_anomalies)
        
        # Save anomalies to database
        if anomalies:
            self.db.add_all(anomalies)
            self.db.commit()
        
        return anomalies
    
    def _detect_new_endpoints(self):
        """Detect new endpoints that haven't been seen before"""
        # Get recent requests (last hour)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        recent_requests = self.db.query(ApiRequest).filter(
            ApiRequest.project_id == self.project_id,
            ApiRequest.created_at >= recent_time
        ).all()
        
        # Get all unique endpoints seen before the recent period
        known_endpoints = set()
        old_endpoints = self.db.query(
            ApiRequest.method, ApiRequest.path
        ).filter(
            ApiRequest.project_id == self.project_id,
            ApiRequest.created_at < recent_time
        ).distinct().all()
        
        for method, path in old_endpoints:
            known_endpoints.add(f"{method}:{path}")
        
        # Check for new endpoints
        anomalies = []
        seen_new_endpoints = set()
        
        for request in recent_requests:
            endpoint_key = f"{request.method}:{request.path}"
            
            if endpoint_key not in known_endpoints and endpoint_key not in seen_new_endpoints:
                seen_new_endpoints.add(endpoint_key)
                
                anomaly = Anomaly(
                    id=uuid.uuid4(),
                    project_id=self.project_id,
                    type=AnomalyType.NEW_ENDPOINT,
                    endpoint_path=request.path,
                    message=f"New endpoint detected: {request.method} {request.path}",
                    severity=AnomalySeverity.LOW
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_rate_limit_violations(self):
        """Detect excessive requests from the same IP in a short time window"""
        # Define thresholds
        time_window = datetime.utcnow() - timedelta(minutes=1)
        request_threshold = 100  # Example: 100 requests per minute
        
        # Get IPs with request counts
        ip_counts = self.db.query(
            ApiRequest.ip, func.count(ApiRequest.id).label("request_count")
        ).filter(
            ApiRequest.project_id == self.project_id,
            ApiRequest.created_at >= time_window
        ).group_by(ApiRequest.ip).having(
            func.count(ApiRequest.id) > request_threshold
        ).all()
        
        # Create anomalies for IPs exceeding threshold
        anomalies = []
        
        for ip, count in ip_counts:
            severity = AnomalySeverity.MEDIUM
            if count > request_threshold * 2:
                severity = AnomalySeverity.HIGH
            
            anomaly = Anomaly(
                id=uuid.uuid4(),
                project_id=self.project_id,
                type=AnomalyType.RATE_LIMIT,
                ip=ip,
                message=f"Rate limit exceeded: {count} requests in 1 minute from IP {ip}",
                severity=severity
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_error_spikes(self):
        """Detect spikes in error responses for endpoints"""
        # Define thresholds
        time_window = datetime.utcnow() - timedelta(minutes=5)
        error_threshold = 0.2  # 20% error rate
        min_requests = 10  # Minimum requests to consider
        
        # Get endpoints with error counts and total counts
        endpoints = self.db.query(
            ApiRequest.method,
            ApiRequest.path,
            func.count(ApiRequest.id).label("total_count"),
            func.sum(case((ApiRequest.status_code >= 500, 1), else_=0)).label("error_count")
        ).filter(
            ApiRequest.project_id == self.project_id,
            ApiRequest.created_at >= time_window
        ).group_by(ApiRequest.method, ApiRequest.path).all()
        
        # Create anomalies for endpoints with high error rates
        anomalies = []
        
        for method, path, total_count, error_count in endpoints:
            if total_count < min_requests:
                continue
            
            error_rate = error_count / total_count
            
            if error_rate >= error_threshold:
                severity = AnomalySeverity.MEDIUM
                if error_rate >= 0.5:  # 50% or more errors
                    severity = AnomalySeverity.HIGH
                
                anomaly = Anomaly(
                    id=uuid.uuid4(),
                    project_id=self.project_id,
                    type=AnomalyType.ERROR_SPIKE,
                    endpoint_path=path,
                    message=f"Error spike detected: {error_count}/{total_count} requests to {method} {path} returned 5xx errors",
                    severity=severity
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _detect_suspicious_locations(self):
        """Detect access from suspicious countries"""
        # Get recent requests from suspicious countries
        recent_time = datetime.utcnow() - timedelta(hours=24)
        suspicious_requests = self.db.query(ApiRequest).filter(
            ApiRequest.project_id == self.project_id,
            ApiRequest.created_at >= recent_time,
            ApiRequest.country_code.in_(self.suspicious_countries)
        ).all()
        
        # Create anomalies for suspicious requests
        anomalies = []
        seen_ips = set()
        
        for request in suspicious_requests:
            if request.ip in seen_ips:
                continue
            
            seen_ips.add(request.ip)
            
            anomaly = Anomaly(
                id=uuid.uuid4(),
                project_id=self.project_id,
                type=AnomalyType.SUSPICIOUS_LOCATION,
                ip=request.ip,
                endpoint_path=request.path,
                message=f"Access from suspicious location: {request.country_code} (IP: {request.ip})",
                severity=AnomalySeverity.HIGH
            )
            anomalies.append(anomaly)
        
        return anomalies