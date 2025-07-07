const axios = require('axios');
const geoip = require('geoip-lite');

/**
 * API Sentinel SDK for Node.js
 * 
 * This middleware captures API request/response metadata and sends it to the
 * API Sentinel backend for analysis and monitoring.
 * 
 * @param {Object} options - Configuration options
 * @param {string} options.apiKey - API Sentinel API key
 * @param {string} options.apiUrl - API Sentinel backend URL (optional)
 * @param {number} options.batchSize - Number of requests to batch (optional)
 * @param {number} options.batchInterval - Batch interval in milliseconds (optional)
 * @param {Array<string>} options.ignorePaths - Paths to ignore (optional)
 * @param {Array<string>} options.sensitiveHeaders - Headers to sanitize (optional)
 * @param {Array<string>} options.sensitiveParams - Query parameters to sanitize (optional)
 * @returns {Function} Express middleware
 */
function sentinel(options) {
  // Default options
  const config = {
    apiKey: options.apiKey,
    apiUrl: options.apiUrl || 'https://api.apisentinel.com',
    batchSize: options.batchSize || 10,
    batchInterval: options.batchInterval || 3000,
    ignorePaths: options.ignorePaths || [],
    sensitiveHeaders: options.sensitiveHeaders || ['authorization', 'cookie', 'set-cookie'],
    sensitiveParams: options.sensitiveParams || ['password', 'token', 'key', 'secret', 'auth']
  };

  // Validate API key
  if (!config.apiKey) {
    throw new Error('API Sentinel: API key is required');
  }

  // Request queue
  let requestQueue = [];
  let timer = null;

  // Send batched requests to API Sentinel
  const sendBatch = async () => {
    if (requestQueue.length === 0) {
      return;
    }

    const batch = [...requestQueue];
    requestQueue = [];

    try {
      await axios.post(`${config.apiUrl}/api/ingest`, {
        requests: batch
      }, {
        headers: {
          'Authorization': `Bearer ${config.apiKey}`,
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      console.error('API Sentinel: Error sending batch', error.message);
      // Add requests back to queue if sending fails
      requestQueue = [...batch, ...requestQueue];
    }
  };

  // Start batch timer
  const startTimer = () => {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(sendBatch, config.batchInterval);
  };

  // Sanitize headers
  const sanitizeHeaders = (headers) => {
    const sanitized = { ...headers };
    
    for (const key in sanitized) {
      if (config.sensitiveHeaders.includes(key.toLowerCase())) {
        sanitized[key] = '[REDACTED]';
      }
    }
    
    return sanitized;
  };

  // Sanitize query parameters
  const sanitizeQueryParams = (query) => {
    const sanitized = { ...query };
    
    for (const key in sanitized) {
      if (config.sensitiveParams.some(param => key.toLowerCase().includes(param.toLowerCase()))) {
        sanitized[key] = '[REDACTED]';
      }
    }
    
    return sanitized;
  };

  // Express middleware
  return (req, res, next) => {
    // Skip ignored paths
    if (config.ignorePaths.some(path => req.path.startsWith(path))) {
      return next();
    }

    // Record start time
    const startTime = Date.now();

    // Store original end method
    const originalEnd = res.end;

    // Override end method to capture response
    res.end = function(chunk, encoding) {
      // Restore original end method
      res.end = originalEnd;

      // Calculate latency
      const latency = Date.now() - startTime;

      // Get client IP
      const ip = req.headers['x-forwarded-for'] || 
                 req.connection.remoteAddress || 
                 req.socket.remoteAddress || 
                 req.connection.socket.remoteAddress;

      // Get country code from IP
      const geo = geoip.lookup(ip);
      const countryCode = geo ? geo.country : null;

      // Create request log
      const requestLog = {
        method: req.method,
        path: req.path,
        query_params: sanitizeQueryParams(req.query),
        headers: sanitizeHeaders(req.headers),
        status_code: res.statusCode,
        latency_ms: latency,
        ip: ip,
        user_agent: req.headers['user-agent'],
        country_code: countryCode
      };

      // Add to queue
      requestQueue.push(requestLog);

      // Send batch if queue is full
      if (requestQueue.length >= config.batchSize) {
        sendBatch();
      } else {
        startTimer();
      }

      // Call original end method
      return originalEnd.call(this, chunk, encoding);
    };

    next();
  };
}

module.exports = sentinel;