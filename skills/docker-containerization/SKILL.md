---
name: docker-containerization
description: This skill should be used when containerizing applications with Docker, creating Dockerfiles, docker-compose configurations, or deploying containers to various platforms. Ideal for Next.js, React, Node.js applications requiring containerization for development, production, or CI/CD pipelines. Use this skill when users need Docker configurations, multi-stage builds, container orchestration, or deployment to Kubernetes, ECS, Cloud Run, etc.
---

# Docker Containerization Skill

## Overview

Generate production-ready Docker configurations for modern web applications, particularly Next.js and Node.js projects. This skill provides Dockerfiles, docker-compose setups, bash scripts for container management, and comprehensive deployment guides for various orchestration platforms.

## Core Capabilities

### 1. Dockerfile Generation

Create optimized Dockerfiles for different environments:

**Production** (`assets/Dockerfile.production`):
- Multi-stage build reducing image size by 85%
- Alpine Linux base (~180MB final image)
- Non-root user execution for security
- Health checks and resource limits

**Development** (`assets/Dockerfile.development`):
- Hot reload support
- All dev dependencies included
- Volume mounts for live code updates

**Nginx Static** (`assets/Dockerfile.nginx`):
- Static export optimization
- Nginx reverse proxy included
- Smallest possible footprint

### 2. Docker Compose Configuration

Multi-container orchestration with `assets/docker-compose.yml`:
- Development and production services
- Network and volume management
- Health checks and logging
- Restart policies

### 3. Bash Scripts for Container Management

**docker-build.sh** - Build images with comprehensive options:
```bash
./docker-build.sh -e prod -t v1.0.0
./docker-build.sh -n my-app --no-cache --platform linux/amd64
```

**docker-run.sh** - Run containers with full configuration:
```bash
./docker-run.sh -i my-app -t v1.0.0 -d
./docker-run.sh -p 8080:3000 --env-file .env.production
```

**docker-push.sh** - Push to registries (Docker Hub, ECR, GCR, ACR):
```bash
./docker-push.sh -n my-app -t v1.0.0 --repo username/my-app
./docker-push.sh -r gcr.io/project --repo my-app --also-tag stable
```

**docker-cleanup.sh** - Free disk space:
```bash
./docker-cleanup.sh --all --dry-run  # Preview cleanup
./docker-cleanup.sh --containers --images  # Clean specific resources
```

### 4. Configuration Files

- **`.dockerignore`**: Excludes unnecessary files (node_modules, .git, logs)
- **`nginx.conf`**: Production-ready Nginx configuration with compression, caching, security headers

### 5. Reference Documentation

**docker-best-practices.md** covers:
- Multi-stage builds explained
- Image optimization techniques (50-85% size reduction)
- Security best practices (non-root users, vulnerability scanning)
- Performance optimization
- Health checks and logging
- Troubleshooting guide

**container-orchestration.md** covers deployment to:
- Docker Compose (local development)
- Kubernetes (enterprise scale with auto-scaling)
- Amazon ECS (AWS-native orchestration)
- Google Cloud Run (serverless containers)
- Azure Container Instances
- Digital Ocean App Platform

Includes configuration examples, commands, auto-scaling setup, and monitoring.

## Workflow Decision Tree

### 1. What environment?
- **Development** → `Dockerfile.development` (hot reload, all dependencies)
- **Production** → `Dockerfile.production` (minimal, secure, optimized)
- **Static Export** → `Dockerfile.nginx` (smallest footprint)

### 2. Single or Multi-container?
- **Single** → Generate Dockerfile only
- **Multi** → Generate `docker-compose.yml` (app + database, microservices)

### 3. Which registry?
- **Docker Hub** → `docker.io/username/image`
- **AWS ECR** → `123456789012.dkr.ecr.region.amazonaws.com/image`
- **Google GCR** → `gcr.io/project-id/image`
- **Azure ACR** → `registry.azurecr.io/image`

### 4. Deployment platform?
- **Kubernetes** → See `references/container-orchestration.md` K8s section
- **ECS** → See ECS task definition examples
- **Cloud Run** → See deployment commands
- **Docker Compose** → Use provided compose file

### 5. Optimizations needed?
- **Image size** → Multi-stage builds, Alpine base
- **Build speed** → Layer caching, BuildKit
- **Security** → Non-root user, vulnerability scanning
- **Performance** → Resource limits, health checks

## Usage Examples

### Example 1: Containerize Next.js App for Production

**User**: "Containerize my Next.js app for production"

**Steps**:
1. Copy `assets/Dockerfile.production` to project root as `Dockerfile`
2. Copy `assets/.dockerignore` to project root
3. Build: `./docker-build.sh -e prod -n my-app -t v1.0.0`
4. Test: `./docker-run.sh -i my-app -t v1.0.0 -p 3000:3000 -d`
5. Push: `./docker-push.sh -n my-app -t v1.0.0 --repo username/my-app`

### Example 2: Development with Docker Compose

**User**: "Set up Docker Compose for local development"

**Steps**:
1. Copy `assets/Dockerfile.development` and `assets/docker-compose.yml` to project
2. Customize services in docker-compose.yml
3. Start: `docker-compose up -d`
4. Logs: `docker-compose logs -f app-dev`

### Example 3: Deploy to Kubernetes

**User**: "Deploy my containerized app to Kubernetes"

**Steps**:
1. Build and push image to registry
2. Review `references/container-orchestration.md` Kubernetes section
3. Create K8s manifests (deployment, service, ingress)
4. Apply: `kubectl apply -f deployment.yaml`
5. Verify: `kubectl get pods && kubectl logs -f deployment/app`

### Example 4: Deploy to AWS ECS

**User**: "Deploy to AWS ECS Fargate"

**Steps**:
1. Build and push to ECR
2. Review `references/container-orchestration.md` ECS section
3. Create task definition JSON
4. Register: `aws ecs register-task-definition --cli-input-json file://task-def.json`
5. Create service: `aws ecs create-service --cluster my-cluster --service-name app --desired-count 3`

## Best Practices

### Security
✅ Use multi-stage builds for production
✅ Run as non-root user
✅ Use specific image tags (not `latest`)
✅ Scan for vulnerabilities
✅ Never hardcode secrets
✅ Implement health checks

### Performance
✅ Optimize layer caching order
✅ Use Alpine images (~85% smaller)
✅ Enable BuildKit for parallel builds
✅ Set resource limits
✅ Use compression

### Maintainability
✅ Add comments for complex steps
✅ Use build arguments for flexibility
✅ Keep Dockerfiles DRY
✅ Version control all configs
✅ Document environment variables

## Troubleshooting

**Image too large (>500MB)**
→ Use multi-stage builds, Alpine base, comprehensive .dockerignore

**Build is slow**
→ Optimize layer caching, use BuildKit, review dependencies

**Container exits immediately**
→ Check logs: `docker logs container-name`
→ Verify CMD/ENTRYPOINT, check port conflicts

**Changes not reflecting**
→ Rebuild without cache, check .dockerignore, verify volume mounts

## Quick Reference

```bash
# Build
./docker-build.sh -e prod -t latest

# Run
./docker-run.sh -i app -t latest -d

# Logs
docker logs -f app

# Execute
docker exec -it app sh

# Cleanup
./docker-cleanup.sh --all --dry-run  # Preview
./docker-cleanup.sh --all            # Execute
```

## Integration with CI/CD

### GitHub Actions
```yaml
- run: |
    chmod +x docker-build.sh docker-push.sh
    ./docker-build.sh -e prod -t ${{ github.sha }}
    ./docker-push.sh -n app -t ${{ github.sha }} --repo username/app
```

### GitLab CI
```yaml
build:
  script:
    - chmod +x docker-build.sh
    - ./docker-build.sh -e prod -t $CI_COMMIT_SHA
```

## Resources

### Scripts (`scripts/`)
Production-ready bash scripts with comprehensive features:
- `docker-build.sh` - Build images (400+ lines, colorized output)
- `docker-run.sh` - Run containers (400+ lines, auto conflict resolution)
- `docker-push.sh` - Push to registries (multi-registry support)
- `docker-cleanup.sh` - Clean resources (dry-run mode, selective cleanup)

### References (`references/`)
Detailed documentation loaded as needed:
- `docker-best-practices.md` - Comprehensive Docker best practices (~500 lines)
- `container-orchestration.md` - Deployment guides for 6+ platforms (~600 lines)

### Assets (`assets/`)
Ready-to-use templates:
- `Dockerfile.production` - Multi-stage production Dockerfile
- `Dockerfile.development` - Development Dockerfile
- `Dockerfile.nginx` - Static export with Nginx
- `docker-compose.yml` - Multi-container orchestration
- `.dockerignore` - Optimized exclusion rules
- `nginx.conf` - Production Nginx configuration
