# Docker Best Practices for Next.js Applications

This document outlines best practices for Docker containerization of Next.js applications.

## Multi-Stage Builds

### Why Use Multi-Stage Builds?

Multi-stage builds create smaller, more secure images by:
- Separating build dependencies from runtime dependencies
- Reducing final image size (often 50-70% smaller)
- Improving security by excluding build tools from production
- Faster deployments due to smaller images

### Stage Structure

**Stage 1: Dependencies**
- Install production dependencies only
- Use `npm ci` for reproducible builds
- Cache dependencies for faster rebuilds

**Stage 2: Builder**
- Copy dependencies from Stage 1
- Build the application
- Generate optimized production assets

**Stage 3: Runner**
- Copy only necessary files (public, .next)
- Run as non-root user
- Minimal runtime dependencies

## Image Optimization

### 1. Base Image Selection

```dockerfile
# ✅ Good: Alpine images (smallest)
FROM node:18-alpine

# ⚠️ Okay: Slim images (small)
FROM node:18-slim

# ❌ Avoid: Full images (large)
FROM node:18
```

**Comparison**:
- Alpine: ~170MB
- Slim: ~250MB
- Full: ~900MB

### 2. Layer Caching

Order Dockerfile instructions from least to most frequently changing:

```dockerfile
# 1. System dependencies (rarely changes)
RUN apk add --no-cache libc6-compat

# 2. Package files (changes occasionally)
COPY package.json package-lock.json ./

# 3. Dependencies (changes when package files change)
RUN npm ci

# 4. Source code (changes frequently)
COPY . .

# 5. Build (changes with source)
RUN npm run build
```

### 3. .dockerignore

Always include a `.dockerignore` file to exclude:
- `node_modules/`
- `.next/`
- `.git/`
- `*.log`
- Development files
- Documentation

**Benefits**:
- Faster builds (less data to copy)
- Smaller images
- Better security (no secrets)

## Security Best Practices

### 1. Run as Non-Root User

```dockerfile
# Create user and group
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Change ownership
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs
```

**Why**: Root users can compromise the host system if container is breached.

### 2. Use Specific Image Tags

```dockerfile
# ✅ Good: Specific version
FROM node:18.17.0-alpine

# ❌ Bad: Latest (unpredictable)
FROM node:latest
```

### 3. Scan for Vulnerabilities

```bash
# Scan image for vulnerabilities
docker scan nextjs-app:latest

# Use Trivy
trivy image nextjs-app:latest
```

### 4. Minimize Attack Surface

- Use minimal base images (Alpine)
- Include only necessary dependencies
- Remove package managers if not needed
- Disable unnecessary services

## Performance Optimization

### 1. Build Cache

Use BuildKit for better caching:

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with cache
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t app:latest .
```

### 2. Parallel Builds

```dockerfile
# Use experimental syntax for parallel operations
# syntax=docker/dockerfile:1.4

FROM node:18-alpine AS deps
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

### 3. Compression

Enable compression in Next.js:

```javascript
// next.config.js
module.exports = {
  compress: true,
}
```

## Environment Variables

### Build-time vs Runtime

**Build-time** (--build-arg):
```dockerfile
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV
```

**Runtime** (docker run -e):
```bash
docker run -e API_URL=https://api.example.com app:latest
```

### Secrets Management

```bash
# ❌ Never do this
ENV API_SECRET=my-secret-key

# ✅ Use secrets
docker run --env-file .env.production app:latest

# ✅ Or use Docker secrets (Swarm)
docker secret create api_key ./api_key.txt
```

## Health Checks

### Application Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
```

### Health Check Endpoint

```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'healthy' }, { status: 200 });
}
```

## Logging

### Container Logs

```bash
# View logs
docker logs -f container-name

# Follow logs from multiple containers
docker-compose logs -f

# Last 100 lines
docker logs --tail 100 container-name
```

### Logging Best Practices

1. **Log to STDOUT/STDERR**: Docker captures these automatically
2. **Structured Logging**: Use JSON format for easy parsing
3. **Log Levels**: Use appropriate levels (error, warn, info, debug)
4. **Avoid Sensitive Data**: Never log secrets or PII

## Networking

### Container Communication

```yaml
# docker-compose.yml
networks:
  app-network:
    driver: bridge

services:
  app:
    networks:
      - app-network

  db:
    networks:
      - app-network
```

### Port Mapping

```bash
# Single port
docker run -p 3000:3000 app:latest

# Multiple ports
docker run -p 3000:3000 -p 9229:9229 app:latest

# Random host port
docker run -p 3000 app:latest
```

## Persistent Data

### Volumes

```bash
# Named volume (managed by Docker)
docker run -v app-data:/app/data app:latest

# Bind mount (host directory)
docker run -v $(pwd)/data:/app/data app:latest

# Anonymous volume
docker run -v /app/data app:latest
```

### Volume Best Practices

1. **Use named volumes** for production data
2. **Use bind mounts** for development (hot reload)
3. **Backup volumes** regularly
4. **Set permissions** correctly

## Development vs Production

### Development Configuration

```dockerfile
# Dockerfile.development
FROM node:18-alpine

# Install all dependencies (including dev)
RUN npm install

# Enable hot reload
CMD ["npm", "run", "dev"]
```

### Production Configuration

```dockerfile
# Dockerfile.production
FROM node:18-alpine AS runner

# Install production dependencies only
RUN npm ci --only=production

# Build and optimize
RUN npm run build

# Start production server
CMD ["node", "server.js"]
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build Docker image
  run: docker build -t app:${{ github.sha }} .

- name: Push to registry
  run: docker push app:${{ github.sha }}
```

### Automated Testing

```yaml
- name: Run tests in container
  run: |
    docker build -t app:test -f Dockerfile.test .
    docker run app:test npm test
```

## Monitoring

### Resource Limits

```bash
# Limit memory
docker run -m 512m app:latest

# Limit CPU
docker run --cpus=".5" app:latest

# Both
docker run -m 512m --cpus=".5" app:latest
```

### Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats container-name

# No streaming
docker stats --no-stream
```

## Troubleshooting

### Common Issues

1. **Image too large**
   - Use multi-stage builds
   - Use Alpine base images
   - Add .dockerignore file

2. **Slow builds**
   - Optimize layer caching
   - Use BuildKit
   - Parallelize operations

3. **Container exits immediately**
   - Check logs: `docker logs container-name`
   - Run interactively: `docker run -it app:latest sh`
   - Check CMD/ENTRYPOINT

4. **Port already in use**
   - Find process: `lsof -i :3000`
   - Use different port: `-p 3001:3000`
   - Stop conflicting container

## Size Comparison

### Before Optimization

```
Repository    Tag       Size
nextjs-app    latest    1.2GB
```

### After Optimization

```
Repository    Tag       Size
nextjs-app    latest    180MB
```

**Savings**: 85% reduction in image size

## Checklist

Before deploying to production, ensure:

- ✅ Using multi-stage builds
- ✅ Running as non-root user
- ✅ Using specific image tags (not latest)
- ✅ .dockerignore file present
- ✅ Health checks configured
- ✅ Resource limits set
- ✅ Logging to STDOUT/STDERR
- ✅ Secrets not hardcoded
- ✅ Image scanned for vulnerabilities
- ✅ Tested in staging environment

---

**Last Updated**: November 2025
**Version**: 1.0.0
