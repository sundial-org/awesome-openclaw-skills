# Container Orchestration Guide

This document covers deploying Dockerized Next.js applications to various orchestration platforms.

## Docker Compose

### Basic Setup

Docker Compose is ideal for:
- Local development environments
- Small-scale deployments
- Testing multi-container setups

### Production Example

```yaml
version: '3.8'

services:
  app:
    image: nextjs-app:latest
    container_name: nextjs-prod
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  app-network:
    driver: bridge
```

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale app=3

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## Kubernetes (K8s)

### When to Use Kubernetes

Use Kubernetes for:
- Large-scale deployments (100+ containers)
- High availability requirements
- Complex microservices architectures
- Auto-scaling needs
- Multi-cloud deployments

### Deployment Configuration

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nextjs-app
  labels:
    app: nextjs-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nextjs-app
  template:
    metadata:
      labels:
        app: nextjs-app
    spec:
      containers:
      - name: nextjs
        image: nextjs-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Configuration

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: nextjs-service
spec:
  selector:
    app: nextjs-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: LoadBalancer
```

### Ingress Configuration

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nextjs-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - app.example.com
    secretName: nextjs-tls
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nextjs-service
            port:
              number: 80
```

### Kubernetes Commands

```bash
# Apply configurations
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/nextjs-app

# Scale deployment
kubectl scale deployment nextjs-app --replicas=5

# Update image
kubectl set image deployment/nextjs-app nextjs=nextjs-app:v2.0.0

# Rollback
kubectl rollout undo deployment/nextjs-app

# Delete resources
kubectl delete -f deployment.yaml
```

## Amazon ECS (Elastic Container Service)

### Task Definition

```json
{
  "family": "nextjs-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "nextjs",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/nextjs-app:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nextjs-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:3000/api/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### ECS Commands

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster my-cluster \
  --service-name nextjs-service \
  --task-definition nextjs-app:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345]}"

# Update service
aws ecs update-service \
  --cluster my-cluster \
  --service nextjs-service \
  --task-definition nextjs-app:2

# Scale service
aws ecs update-service \
  --cluster my-cluster \
  --service nextjs-service \
  --desired-count 5
```

## Google Cloud Run

### Deployment

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/nextjs-app

# Deploy to Cloud Run
gcloud run deploy nextjs-app \
  --image gcr.io/PROJECT_ID/nextjs-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars NODE_ENV=production
```

### Cloud Run YAML

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: nextjs-app
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: '10'
        autoscaling.knative.dev/minScale: '1'
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/nextjs-app
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: production
        resources:
          limits:
            memory: 512Mi
            cpu: '1'
```

## Azure Container Instances (ACI)

### Deployment

```bash
# Create resource group
az group create --name myResourceGroup --location eastus

# Create container
az container create \
  --resource-group myResourceGroup \
  --name nextjs-app \
  --image myregistry.azurecr.io/nextjs-app:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server myregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --dns-name-label nextjs-app-unique \
  --ports 3000
```

## Digital Ocean App Platform

### App Spec

```yaml
# .do/app.yaml
name: nextjs-app
services:
- name: web
  github:
    repo: username/nextjs-app
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile.production
  http_port: 3000
  instance_count: 3
  instance_size_slug: basic-s
  env_vars:
  - key: NODE_ENV
    value: "production"
  health_check:
    http_path: /api/health
    initial_delay_seconds: 30
    period_seconds: 10
    timeout_seconds: 5
    success_threshold: 1
    failure_threshold: 3
```

## Comparison Matrix

| Platform | Best For | Complexity | Cost | Auto-Scaling |
|----------|----------|------------|------|--------------|
| Docker Compose | Dev/Small deployments | Low | Very Low | No |
| Kubernetes | Enterprise/Large scale | High | Medium | Yes |
| ECS | AWS ecosystem | Medium | Medium | Yes |
| Cloud Run | Serverless/Pay-per-use | Low | Low | Yes |
| ACI | Simple Azure deployments | Low | Medium | Limited |
| DO App Platform | Simple deployments | Low | Low | Yes |

## Auto-Scaling Configuration

### Kubernetes HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nextjs-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nextjs-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### ECS Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/my-cluster/nextjs-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-cluster/nextjs-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    "TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}"
```

## Load Balancing

### Nginx Load Balancer

```nginx
upstream nextjs_backend {
    least_conn;
    server app1:3000 weight=3;
    server app2:3000 weight=2;
    server app3:3000 weight=1;
}

server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://nextjs_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Monitoring & Logging

### Prometheus + Grafana (Kubernetes)

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nextjs-app
spec:
  selector:
    matchLabels:
      app: nextjs-app
  endpoints:
  - port: metrics
    interval: 30s
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
```

## Disaster Recovery

### Backup Strategies

1. **Container Images**: Store in multiple registries
2. **Data Volumes**: Regular snapshots
3. **Configuration**: Version control (Git)
4. **Secrets**: Encrypted backups

### High Availability

```yaml
# Kubernetes with pod anti-affinity
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchExpressions:
        - key: app
          operator: In
          values:
          - nextjs-app
      topologyKey: kubernetes.io/hostname
```

---

**Last Updated**: November 2025
**Version**: 1.0.0
