# API Sentinel SDK for Node.js

This SDK allows you to monitor and secure your Node.js API by capturing request/response metadata and sending it to the API Sentinel platform for analysis.

## Installation

```bash
npm install @apisentinel/sdk
```

## Usage

### Express.js

```javascript
const express = require('express');
const sentinel = require('@apisentinel/sdk');

const app = express();

// Add API Sentinel middleware
app.use(sentinel({
  apiKey: 'your-api-key'
}));

// Your routes
app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

## Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `apiKey` | string | **Required**. Your API Sentinel API key | - |
| `apiUrl` | string | API Sentinel backend URL | `https://api.apisentinel.com` |
| `batchSize` | number | Number of requests to batch before sending | `10` |
| `batchInterval` | number | Maximum time (ms) to wait before sending a batch | `3000` |
| `ignorePaths` | string[] | Paths to exclude from monitoring | `[]` |
| `sensitiveHeaders` | string[] | Headers to sanitize in logs | `['authorization', 'cookie', 'set-cookie']` |
| `sensitiveParams` | string[] | Query parameters to sanitize in logs | `['password', 'token', 'key', 'secret', 'auth']` |

## Advanced Configuration

```javascript
app.use(sentinel({
  apiKey: 'your-api-key',
  apiUrl: 'https://your-custom-api-sentinel-instance.com',
  batchSize: 20,
  batchInterval: 5000,
  ignorePaths: ['/health', '/metrics'],
  sensitiveHeaders: ['authorization', 'x-api-key'],
  sensitiveParams: ['password', 'secret']
}));
```

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