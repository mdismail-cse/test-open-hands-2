# API Sentinel SDK for Python

This SDK allows you to monitor and secure your Python API by capturing request/response metadata and sending it to the API Sentinel platform for analysis.

## Installation

```bash
pip install apisentinel
```

## Usage

### Flask

```python
from flask import Flask
from apisentinel.flask import SentinelMiddleware

app = Flask(__name__)

# Add API Sentinel middleware
app.wsgi_app = SentinelMiddleware(
    app.wsgi_app,
    api_key="your-api-key"
)

@app.route("/api/users")
def get_users():
    return {"users": []}

if __name__ == "__main__":
    app.run(debug=True)
```

### Django

```python
# In your Django settings.py
MIDDLEWARE = [
    # ... other middleware
    "apisentinel.django.SentinelMiddleware",
]

# API Sentinel configuration
API_SENTINEL = {
    "api_key": "your-api-key",
    # Optional settings
    "api_url": "https://api.apisentinel.com",
    "batch_size": 10,
    "batch_interval": 3,  # seconds
    "ignore_paths": ["/admin/", "/health/"],
    "sensitive_headers": ["authorization", "cookie"],
    "sensitive_params": ["password", "token"],
}
```

### FastAPI

```python
from fastapi import FastAPI
from apisentinel.fastapi import SentinelMiddleware

app = FastAPI()

# Add API Sentinel middleware
app.add_middleware(
    SentinelMiddleware,
    api_key="your-api-key"
)

@app.get("/api/users")
def get_users():
    return {"users": []}
```

## Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `api_key` | str | **Required**. Your API Sentinel API key | - |
| `api_url` | str | API Sentinel backend URL | `https://api.apisentinel.com` |
| `batch_size` | int | Number of requests to batch before sending | `10` |
| `batch_interval` | int | Maximum time (seconds) to wait before sending a batch | `3` |
| `ignore_paths` | list | Paths to exclude from monitoring | `[]` |
| `sensitive_headers` | list | Headers to sanitize in logs | `['authorization', 'cookie', 'set-cookie']` |
| `sensitive_params` | list | Query parameters to sanitize in logs | `['password', 'token', 'key', 'secret', 'auth']` |

## What Data is Collected?

The SDK collects the following metadata for each API request:

- HTTP Method (GET, POST, etc.)
- Path (e.g., /api/login)
- Query parameters (sensitive keys obfuscated)
- Response status code (e.g., 200, 401, 500)
- Latency (in ms)
- Headers (sensitive headers sanitized)
- IP address
- User-Agent string
- Country code (via IP geolocation)

No request bodies or response payloads are collected to ensure data privacy.

## License

MIT