# Rate Limiting Guide

## Recommended Limits

| Endpoint | Limit | Window | Rationale |
|----------|-------|--------|-----------|
| `POST /challenge` | 10 | 1 minute | Prevent challenge flooding |
| `POST /verify` | 10 | 1 minute | Prevent brute force |
| Failed verifications | 5 | 1 minute | Slow down attackers |
| Per IP | 60 | 1 minute | Overall protection |

## Implementation

### Using express-rate-limit

```bash
npm install express-rate-limit
```

```javascript
import rateLimit from 'express-rate-limit';

// General rate limit
const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 60,
  message: { error: 'Too many requests', retryAfter: 60 },
  standardHeaders: true,
  legacyHeaders: false
});

// Stricter limit for challenge endpoint
const challengeLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { error: 'Too many challenge requests', retryAfter: 60 }
});

// Stricter limit for verify endpoint
const verifyLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  message: { error: 'Too many verification attempts', retryAfter: 60 }
});

// Failed verification tracker
const failedAttempts = new Map();

const failureLimiter = (req, res, next) => {
  const ip = req.ip;
  const now = Date.now();
  const windowMs = 60 * 1000;
  
  // Clean old entries
  const attempts = (failedAttempts.get(ip) || [])
    .filter(t => now - t < windowMs);
  
  if (attempts.length >= 5) {
    return res.status(429).json({
      error: 'Too many failed attempts',
      retryAfter: Math.ceil((attempts[0] + windowMs - now) / 1000)
    });
  }
  
  // Store original json method
  const originalJson = res.json.bind(res);
  res.json = (body) => {
    if (body && body.verified === false) {
      attempts.push(now);
      failedAttempts.set(ip, attempts);
    }
    return originalJson(body);
  };
  
  next();
};

// Apply limiters
app.use('/aap', generalLimiter);
app.use('/aap/v1/challenge', challengeLimiter);
app.use('/aap/v1/verify', verifyLimiter, failureLimiter);
```

### Using Redis (for distributed systems)

```bash
npm install rate-limit-redis ioredis
```

```javascript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

const limiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.call(...args),
    prefix: 'aap-ratelimit:'
  }),
  windowMs: 60 * 1000,
  max: 60
});

app.use('/aap', limiter);
```

## Response Headers

When rate limited, include these headers:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706745660
```

## Client Handling

Clients should handle rate limits gracefully:

```javascript
async function verifyWithRetry(client, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await client.verify();
    } catch (error) {
      if (error.status === 429) {
        const retryAfter = error.retryAfter || 60;
        console.log(`Rate limited. Waiting ${retryAfter}s...`);
        await new Promise(r => setTimeout(r, retryAfter * 1000));
      } else {
        throw error;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Monitoring

Track these metrics:

| Metric | Alert Threshold |
|--------|-----------------|
| Rate limit hits/min | > 100 |
| Failed verifications/min | > 50 |
| Unique IPs hitting limits | > 20 |
| 429 responses % | > 10% |

## IP Considerations

- Use `X-Forwarded-For` header when behind proxy
- Consider API keys for higher limits
- Whitelist known good actors if needed

```javascript
app.set('trust proxy', 1); // Trust first proxy

const limiter = rateLimit({
  keyGenerator: (req) => {
    // Use API key if present, otherwise IP
    return req.headers['x-api-key'] || req.ip;
  },
  // Higher limit for API key users
  max: (req) => req.headers['x-api-key'] ? 200 : 60
});
```
