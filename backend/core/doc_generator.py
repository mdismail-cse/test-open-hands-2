from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import uuid
import json
import os
from typing import Dict, List, Any
import openai

from core.models import ApiRequest, ApiDoc, Project

class OpenAPIGenerator:
    def __init__(self, db: Session, project_id: uuid.UUID):
        self.db = db
        self.project_id = project_id
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
    
    def generate_openapi_spec(self):
        """
        Generate OpenAPI specification from API request logs
        
        This method analyzes API request logs and uses GPT to generate
        an OpenAPI specification document.
        """
        # Get project info
        project = self.db.query(Project).filter(Project.id == self.project_id).first()
        if not project:
            raise ValueError(f"Project with ID {self.project_id} not found")
        
        # Get unique endpoints
        endpoints = self._get_unique_endpoints()
        
        if not endpoints:
            return None
        
        # Generate OpenAPI spec using GPT
        openapi_spec = self._generate_with_gpt(project.name, endpoints)
        
        # Save to database
        api_doc = ApiDoc(
            id=uuid.uuid4(),
            project_id=self.project_id,
            json_content=openapi_spec
        )
        
        self.db.add(api_doc)
        self.db.commit()
        self.db.refresh(api_doc)
        
        return api_doc
    
    def _get_unique_endpoints(self):
        """Get unique endpoints with their request/response data"""
        # Get distinct method/path combinations
        endpoint_pairs = self.db.query(
            distinct(ApiRequest.method),
            distinct(ApiRequest.path)
        ).filter(
            ApiRequest.project_id == self.project_id
        ).all()
        
        endpoints = []
        
        for method, path in endpoint_pairs:
            # Get sample requests for this endpoint
            sample_requests = self.db.query(ApiRequest).filter(
                ApiRequest.project_id == self.project_id,
                ApiRequest.method == method,
                ApiRequest.path == path
            ).order_by(ApiRequest.created_at.desc()).limit(5).all()
            
            if not sample_requests:
                continue
            
            # Extract status codes
            status_codes = set()
            for req in sample_requests:
                status_codes.add(req.status_code)
            
            # Extract query parameters
            query_params = {}
            for req in sample_requests:
                if req.query_params:
                    for key, value in req.query_params.items():
                        query_params[key] = value
            
            # Extract headers (excluding sensitive ones)
            headers = {}
            for req in sample_requests:
                if req.headers:
                    for key, value in req.headers.items():
                        if key.lower() not in ["authorization", "cookie"]:
                            headers[key] = value
            
            # Create endpoint info
            endpoint_info = {
                "method": method,
                "path": path,
                "status_codes": list(status_codes),
                "query_params": query_params,
                "headers": headers
            }
            
            endpoints.append(endpoint_info)
        
        return endpoints
    
    def _generate_with_gpt(self, project_name: str, endpoints: List[Dict[str, Any]]):
        """Generate OpenAPI specification using GPT"""
        # Create prompt
        prompt = f"""
        Based on the following API traffic data, generate a complete OpenAPI 3.0 specification in JSON format.
        
        Project name: {project_name}
        
        Endpoints:
        {json.dumps(endpoints, indent=2)}
        
        Please generate a comprehensive OpenAPI 3.0 specification that includes:
        1. Info section with title, description, and version
        2. Paths section with all endpoints
        3. For each endpoint, include:
           - Summary and description
           - Parameters (path, query, header)
           - Request body schema (if applicable)
           - Response schemas for different status codes
        4. Components section with reusable schemas
        
        Return only valid JSON that conforms to the OpenAPI 3.0 specification.
        """
        
        try:
            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an API documentation expert. Your task is to generate accurate OpenAPI 3.0 specifications based on API traffic data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Extract and parse JSON from response
            openapi_json_str = response.choices[0].message.content.strip()
            
            # Clean up the response to extract just the JSON
            if "```json" in openapi_json_str:
                openapi_json_str = openapi_json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in openapi_json_str:
                openapi_json_str = openapi_json_str.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            openapi_spec = json.loads(openapi_json_str)
            
            return openapi_spec
        
        except Exception as e:
            # Fallback to a basic template if GPT fails
            return self._generate_basic_template(project_name, endpoints)
    
    def _generate_basic_template(self, project_name: str, endpoints: List[Dict[str, Any]]):
        """Generate a basic OpenAPI template without GPT"""
        paths = {}
        
        for endpoint in endpoints:
            method = endpoint["method"].lower()
            path = endpoint["path"]
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = {
                "summary": f"{method.upper()} {path}",
                "description": f"Endpoint for {method.upper()} {path}",
                "parameters": [],
                "responses": {}
            }
            
            # Add query parameters
            if endpoint["query_params"]:
                for param_name in endpoint["query_params"]:
                    paths[path][method]["parameters"].append({
                        "name": param_name,
                        "in": "query",
                        "schema": {
                            "type": "string"
                        }
                    })
            
            # Add responses
            for status_code in endpoint["status_codes"]:
                paths[path][method]["responses"][str(status_code)] = {
                    "description": f"Status code {status_code} response"
                }
        
        # Create OpenAPI spec
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{project_name} API",
                "description": f"API documentation for {project_name}",
                "version": "1.0.0"
            },
            "paths": paths,
            "components": {
                "schemas": {}
            }
        }
        
        return openapi_spec