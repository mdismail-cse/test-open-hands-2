from sqlalchemy.orm import Session
import httpx
import os
from typing import Dict, Any, List
import json
from datetime import datetime

from core.models import Anomaly, Project, AlertChannel

class AlertSystem:
    def __init__(self, db: Session):
        self.db = db
        self.email_provider = os.getenv("EMAIL_PROVIDER", "resend")
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        self.mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    
    async def send_alert(self, anomaly_id: str):
        """
        Send alert for an anomaly
        
        This method sends alerts via configured channels (email, Slack, webhook)
        for a specific anomaly.
        """
        # Get anomaly
        anomaly = self.db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise ValueError(f"Anomaly with ID {anomaly_id} not found")
        
        # Get project
        project = self.db.query(Project).filter(Project.id == anomaly.project_id).first()
        if not project:
            raise ValueError(f"Project with ID {anomaly.project_id} not found")
        
        # Get alert channels for project
        alert_channels = self.db.query(AlertChannel).filter(
            AlertChannel.project_id == project.id,
            AlertChannel.active == True
        ).all()
        
        if not alert_channels:
            return False
        
        # Prepare alert data
        alert_data = {
            "project_name": project.name,
            "anomaly_type": anomaly.type,
            "timestamp": anomaly.created_at.isoformat(),
            "endpoint": anomaly.endpoint_path,
            "ip": str(anomaly.ip) if anomaly.ip else None,
            "message": anomaly.message,
            "severity": anomaly.severity
        }
        
        # Send alerts to all channels
        results = []
        
        for channel in alert_channels:
            if channel.type == "email":
                result = await self._send_email_alert(channel.config, alert_data)
                results.append(result)
            
            elif channel.type == "slack":
                result = await self._send_slack_alert(channel.config, alert_data)
                results.append(result)
            
            elif channel.type == "webhook":
                result = await self._send_webhook_alert(channel.config, alert_data)
                results.append(result)
        
        return all(results)
    
    async def _send_email_alert(self, config: Dict[str, Any], alert_data: Dict[str, Any]):
        """Send alert via email"""
        email = config.get("email")
        if not email:
            return False
        
        # Prepare email content
        subject = f"API Sentinel Alert: {alert_data['severity'].upper()} - {alert_data['anomaly_type']}"
        
        body = f"""
        <h2>API Sentinel Security Alert</h2>
        <p><strong>Project:</strong> {alert_data['project_name']}</p>
        <p><strong>Type:</strong> {alert_data['anomaly_type']}</p>
        <p><strong>Severity:</strong> {alert_data['severity'].upper()}</p>
        <p><strong>Time:</strong> {alert_data['timestamp']}</p>
        <p><strong>Endpoint:</strong> {alert_data['endpoint'] or 'N/A'}</p>
        <p><strong>IP Address:</strong> {alert_data['ip'] or 'N/A'}</p>
        <p><strong>Message:</strong> {alert_data['message']}</p>
        """
        
        try:
            if self.email_provider == "resend":
                return await self._send_resend_email(email, subject, body)
            else:
                return await self._send_mailgun_email(email, subject, body)
        except Exception as e:
            print(f"Error sending email alert: {str(e)}")
            return False
    
    async def _send_resend_email(self, to_email: str, subject: str, body: str):
        """Send email via Resend API"""
        if not self.resend_api_key:
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {self.resend_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "alerts@apisentinel.com",
                    "to": to_email,
                    "subject": subject,
                    "html": body
                }
            )
            
            return response.status_code == 200
    
    async def _send_mailgun_email(self, to_email: str, subject: str, body: str):
        """Send email via Mailgun API"""
        if not self.mailgun_api_key or not self.mailgun_domain:
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"API Sentinel <alerts@{self.mailgun_domain}>",
                    "to": to_email,
                    "subject": subject,
                    "html": body
                }
            )
            
            return response.status_code == 200
    
    async def _send_slack_alert(self, config: Dict[str, Any], alert_data: Dict[str, Any]):
        """Send alert via Slack webhook"""
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            return False
        
        # Prepare Slack message
        severity_emoji = "🟢"
        if alert_data["severity"] == "medium":
            severity_emoji = "🟠"
        elif alert_data["severity"] == "high":
            severity_emoji = "🔴"
        elif alert_data["severity"] == "critical":
            severity_emoji = "⚠️"
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"API Sentinel Alert: {severity_emoji} {alert_data['anomaly_type']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Project:*\n{alert_data['project_name']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{alert_data['severity'].upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time:*\n{alert_data['timestamp']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Endpoint:*\n{alert_data['endpoint'] or 'N/A'}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:*\n{alert_data['message']}"
                    }
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=message
                )
                
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending Slack alert: {str(e)}")
            return False
    
    async def _send_webhook_alert(self, config: Dict[str, Any], alert_data: Dict[str, Any]):
        """Send alert via custom webhook"""
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=alert_data
                )
                
                return response.status_code >= 200 and response.status_code < 300
        except Exception as e:
            print(f"Error sending webhook alert: {str(e)}")
            return False