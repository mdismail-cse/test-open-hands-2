--- /workspace/openhands_workspace/test-open-hands-2/README.md
+++ /workspace/openhands_workspace/test-open-hands-2/README.md
@@ -3,23 +3,248 @@
-API Sentinel is an intelligent API Security & Usage Monitor SaaS platform. It logs API traffic, detects security anomalies, and auto-generates OpenAPI documentation using AI.
-
-## Features
-
-- API traffic monitoring and logging
-- Security anomaly detection
-- AI-powered OpenAPI documentation generation
-- Modern dashboard with clean UX
-- Alert system (Slack/Email/Webhooks)
-
-## Project Structure
-
-- `backend/`: FastAPI application for the backend services
-- `sdk-node/`: Node.js SDK for API monitoring
-- `sdk-python/`: Python SDK for API monitoring
-- `frontend/`: Next.js frontend application
-- `db/`: SQL scripts and migrations
-- `alerts/`: Webhook/email logic
-- `ai-docs/`: GPT integration scripts
-
-## Getting Started
-
-See individual component READMEs for setup and usage instructions.
+<div align="center">
+  <img src="https://via.placeholder.com/200x200?text=API+Sentinel" alt="API Sentinel Logo" width="200" height="200">
+  <h3>Intelligent API Security & Usage Monitor</h3>
+  <p>Monitor, secure, and document your APIs with AI-powered insights</p>
+</div>
+
+## 🌟 What is API Sentinel?
+
+API Sentinel is a developer-friendly platform that helps you monitor, secure, and document your APIs. It works by capturing API traffic data through lightweight SDKs, analyzing the data for security anomalies, and automatically generating OpenAPI documentation using AI.
+
+**Perfect for:**
+- Development teams who want to monitor API usage
+- Security teams looking to detect suspicious API activity
+- Product teams needing up-to-date API documentation
+
+## ✨ Key Features
+
+- **🔍 API Traffic Monitoring**: Track all API requests with detailed metrics (method, path, status, latency)
+- **🛡️ Security Anomaly Detection**: Get alerts for suspicious activity (unusual traffic patterns, access from suspicious locations)
+- **📝 AI-Generated Documentation**: Automatically create and maintain OpenAPI documentation based on actual API usage
+- **📊 Modern Dashboard**: Clean, responsive UI to visualize API traffic and security events
+- **🔔 Customizable Alerts**: Receive notifications via email, Slack, or webhooks
+
+## 🚀 Getting Started (5-Minute Setup)
+
+### Step 1: Create an Account
+
+1. Sign up at [apisentinel.com](https://apisentinel.com) (placeholder)
+2. Create a new project and get your API key
+
+### Step 2: Install the SDK
+
+#### For Node.js (Express) Applications:
+
+```bash
+npm install @apisentinel/sdk
+```
+
+Then add the middleware to your Express app:
+
+```javascript
+const express = require('express');
+const sentinel = require('@apisentinel/sdk');
+
+const app = express();
+
+// Add the middleware before your routes
+app.use(sentinel({
+  apiKey: 'your-api-key-here'
+}));
+
+// Your routes
+app.get('/', (req, res) => {
+  res.send('Hello World!');
+});
+
+app.listen(3000, () => {
+  console.log('Server running on port 3000');
+});
+```
+
+#### For Python Applications:
+
+Install the SDK:
+
+```bash
+pip install apisentinel
+```
+
+##### Flask:
+
+```python
+from flask import Flask
+from apisentinel.flask import SentinelMiddleware
+
+app = Flask(__name__)
+app.wsgi_app = SentinelMiddleware(
+    app.wsgi_app,
+    api_key="your-api-key-here"
+)
+
+@app.route('/')
+def hello_world():
+    return 'Hello, World!'
+
+if __name__ == '__main__':
+    app.run(debug=True)
+```
+
+##### Django:
+
+Add to your settings.py:
+
+```python
+# settings.py
+API_SENTINEL = {
+    "api_key": "your-api-key-here"
+}
+
+MIDDLEWARE = [
+    # ... other middleware
+    "apisentinel.django.SentinelMiddleware",
+    # ... other middleware
+]
+```
+
+##### FastAPI:
+
+```python
+from fastapi import FastAPI
+from apisentinel.fastapi import SentinelMiddleware
+
+app = FastAPI()
+
+app.add_middleware(
+    SentinelMiddleware,
+    api_key="your-api-key-here"
+)
+
+@app.get("/")
+def read_root():
+    return {"Hello": "World"}
+```
+
+### Step 3: View Your Dashboard
+
+1. Go to [dashboard.apisentinel.com](https://dashboard.apisentinel.com) (placeholder)
+2. Log in with your credentials
+3. Select your project to view:
+   - Real-time API traffic
+   - Detected anomalies
+   - Auto-generated API documentation
+
+## 📚 Advanced Configuration
+
+### SDK Options
+
+All SDKs support these common options:
+
+```javascript
+// Node.js example (similar options available in Python)
+app.use(sentinel({
+  apiKey: 'your-api-key-here',
+  apiUrl: 'https://api.apisentinel.com',  // Custom API endpoint
+  batchSize: 10,                          // Number of requests to batch
+  batchInterval: 3,                       // Seconds between batch sends
+  ignorePaths: ['/health', '/metrics'],   // Paths to exclude
+  sensitiveHeaders: ['authorization'],    // Headers to redact
+  sensitiveParams: ['password', 'token']  // Query params to redact
+}));
+```
+
+### Setting Up Alerts
+
+1. Go to your project settings in the dashboard
+2. Navigate to "Alerts"
+3. Configure alert channels:
+   - Email: Add recipient email addresses
+   - Slack: Add webhook URL
+   - Custom webhook: Add your endpoint URL
+
+### Customizing Anomaly Detection
+
+1. Go to your project settings
+2. Navigate to "Anomaly Detection"
+3. Adjust sensitivity levels for different types of anomalies:
+   - Rate limiting thresholds
+   - Error rate thresholds
+   - Geolocation restrictions
+
+## 🛠️ Local Development
+
+If you want to run the entire API Sentinel platform locally:
+
+### Prerequisites
+
+- Node.js 18.x or later
+- Python 3.8 or later
+- PostgreSQL 13 or later
+
+### Backend Setup
+
+```bash
+# Clone the repository
+git clone https://github.com/yourusername/api-sentinel.git
+cd api-sentinel
+
+# Set up environment
+cp .env.example .env
+# Edit .env with your configuration
+
+# Install backend dependencies
+cd backend
+pip install -r requirements.txt
+
+# Start the backend server
+uvicorn main:app --reload
+```
+
+### Frontend Setup
+
+```bash
+# From the project root
+cd frontend
+
+# Install dependencies
+npm install
+
+# Start the development server
+npm run dev
+```
+
+## 📖 Project Structure
+
+```
+api-sentinel/
+├── backend/              # FastAPI app
+│   ├── api/              # Routes
+│   ├── core/             # Processing engine
+│   └── jobs/             # Celery tasks
+├── sdk-node/             # Node.js SDK
+├── sdk-python/           # Python SDK
+├── frontend/             # Next.js frontend app
+├── db/                   # SQL scripts and migrations
+├── .env.example
+└── README.md
+```
+
+## 🤝 Contributing
+
+We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.
+
+## 📄 License
+
+This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
+
+## 🙋 Getting Help
+
+- **Documentation**: [docs.apisentinel.com](https://docs.apisentinel.com) (placeholder)
+- **Issues**: [GitHub Issues](https://github.com/yourusername/api-sentinel/issues)
+- **Community**: [Discord Server](https://discord.gg/apisentinel) (placeholder)
+- **Email**: support@apisentinel.com (placeholder)
+
+---
+
+<div align="center">
+  <p>Made with ❤️ by the API Sentinel Team</p>
+</div>
