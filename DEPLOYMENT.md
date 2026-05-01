# Deployment Guide for Mystnodes Monitor

This guide covers deploying your Mystnodes Monitor full-stack application (React frontend + FastAPI backend + MongoDB).

## Quick Start (Docker Compose - Recommended for Most Users)

### Prerequisites
- Docker and Docker Compose installed
- Git
- A server or local machine to run on

### Step 1: Clone and Setup

```bash
git clone https://github.com/sonnybobo336-ui/Mystnodes-Monitor-.git
cd Mystnodes-Monitor-
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your production values:
```bash
MONGO_ROOT_PASSWORD=your_strong_password_here
SECRET_KEY=your_random_secret_key
JWT_SECRET=your_jwt_secret
```

### Step 3: Deploy

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Step 4: Verify Deployment

```bash
# Check health
curl http://localhost/health

# Check API
curl http://localhost/api/health

# Stop services
docker-compose down
```

## Deployment Options

### Option 1: Docker Compose (Single Server)

**Best for:** Development, small deployments, testing environments

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
```

**Ports:**
- `80` - Nginx (HTTP)
- `8000` - Backend API
- `27017` - MongoDB

### Option 2: Production on VPS/Dedicated Server

#### Prerequisites
- Ubuntu 20.04+ or similar Linux
- SSH access
- 2GB+ RAM
- 10GB+ storage

#### Setup Script

```bash
#!/bin/bash
# setup-production.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
cd ~
git clone https://github.com/sonnybobo336-ui/Mystnodes-Monitor-.git
cd Mystnodes-Monitor-

# Setup environment
cp .env.example .env
# Edit .env with production values
nano .env

# Start services
sudo docker-compose up -d

# Setup SSL with Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to ssl directory
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*

# Uncomment HTTPS block in nginx.conf and restart
docker-compose restart nginx

# Setup auto-renewal
echo "0 3 * * * docker-compose restart nginx" | crontab -
```

### Option 3: Kubernetes (Enterprise/Scaling)

#### Create Kubernetes manifests

**k8s/namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mystnodes
```

**k8s/configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mystnodes-config
  namespace: mystnodes
data:
  API_PREFIX: "/api"
  ENVIRONMENT: "production"
```

**k8s/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mystnodes-backend
  namespace: mystnodes
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mystnodes-backend
  template:
    metadata:
      labels:
        app: mystnodes-backend
    spec:
      containers:
      - name: backend
        image: your-registry/mystnodes:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: mystnodes-secrets
              key: mongodb-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**Deploy to Kubernetes:**
```bash
kubectl create namespace mystnodes
kubectl apply -f k8s/
kubectl get pods -n mystnodes
```

### Option 4: AWS ECS (Amazon Container Service)

#### Prerequisites
- AWS Account
- AWS CLI configured
- ECR repository created

#### Steps

```bash
# 1. Build and push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [YOUR_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com

docker build -t mystnodes:latest .
docker tag mystnodes:latest [YOUR_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/mystnodes:latest
docker push [YOUR_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/mystnodes:latest

# 2. Create ECS task definition
# Update ecs-task-definition.json with your image URI

aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# 3. Create ECS service
aws ecs create-service \
  --cluster mystnodes-cluster \
  --service-name mystnodes-service \
  --task-definition mystnodes-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

## SSL/HTTPS Setup

### Using Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem

# Uncomment HTTPS block in nginx.conf
# Restart Nginx
docker-compose restart nginx

# Auto-renewal cron job
echo "0 3 * * * certbot renew --quiet && docker-compose restart nginx" | sudo crontab -
```

## Monitoring & Maintenance

### Check Service Status

```bash
# View all running containers
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f mongodb
docker-compose logs -f nginx

# View specific service logs with timestamps
docker-compose logs --timestamps backend
```

### Backup MongoDB

```bash
# Backup database
docker-compose exec mongodb mongodump -u admin -p $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin --out /data/db/backup/

# Restore from backup
docker-compose exec mongodb mongorestore -u admin -p $MONGO_ROOT_PASSWORD \
  --authenticationDatabase admin /data/db/backup/
```

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services with new image
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Backend not starting

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - MongoDB not ready: wait a few seconds
# - Port 8000 already in use: change port in docker-compose.yml
# - Missing environment variables: check .env file
```

### MongoDB connection errors

```bash
# Check MongoDB status
docker-compose exec mongodb mongosh

# Verify credentials in .env
# Check network: docker network ls
```

### Nginx not serving requests

```bash
# Test nginx configuration
docker-compose exec nginx nginx -t

# Check logs
docker-compose logs nginx

# Verify backend is running
curl http://localhost:8000/health
```

## Performance Tuning

### Increase MongoDB performance

Edit `docker-compose.yml`:
```yaml
mongodb:
  # Add cache and connection pooling
  command: --wiredTigerCacheSizeGB=1 --maxConnections=1000
```

### Scale backend (with load balancer)

```yaml
backend:
  deploy:
    replicas: 3
  # Behind load balancer for traffic distribution
```

## Security Best Practices

1. **Change default passwords:**
   - MongoDB admin password
   - SECRET_KEY
   - JWT_SECRET

2. **Enable HTTPS:** Use SSL certificates (Let's Encrypt free option)

3. **Restrict MongoDB access:** Only allow connections from backend service

4. **Use environment variables:** Never commit secrets to git

5. **Regular backups:** Automate MongoDB backups

6. **Keep Docker images updated:** Regularly pull latest base images

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review .env configuration
- Ensure all ports are available
- Verify MongoDB is healthy
- Check network connectivity between services

## CI/CD Setup (GitHub Actions)

The repository includes GitHub Actions workflow (`.github/workflows/deploy.yml`) for:
- Automated testing (frontend + backend)
- Building Docker images
- Auto-deploying to server on push to main

### Setup GitHub Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add these secrets:
   - `DEPLOY_KEY`: SSH private key (cat ~/.ssh/id_rsa)
   - `DEPLOY_HOST`: Server IP or domain
   - `DEPLOY_USER`: SSH username on server

The workflow will automatically test and deploy on each push to main branch.
