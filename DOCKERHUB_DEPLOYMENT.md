# Docker Hub Deployment for Men's Health Server

This guide explains how to push your Men's Health Server Docker image to Docker Hub and deploy it.

## Prerequisites

1. **Docker Hub Account**: Create an account at [hub.docker.com](https://hub.docker.com)
2. **Docker Desktop**: Install and run Docker Desktop
3. **Docker CLI**: Ensure Docker CLI is installed and working

## Quick Push to Docker Hub

### 1. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### 2. Configure Username

Edit the push script and replace `walterbanda123` with your Docker Hub username:

```bash
# In push-to-dockerhub.sh, change this line:
DOCKER_HUB_USERNAME="${DOCKER_HUB_USERNAME:-your-dockerhub-username}"
```

Or set it as an environment variable:

```bash
export DOCKER_HUB_USERNAME=your-dockerhub-username
```

### 3. Make Script Executable and Run

```bash
chmod +x push-to-dockerhub.sh
./push-to-dockerhub.sh
```

## Manual Push Process

If you prefer to do it manually:

### 1. Build the Image

```bash
docker build -t mens-health-server:latest .
```

### 2. Tag for Docker Hub

```bash
docker tag mens-health-server:latest your-username/mens-health-server:latest
```

### 3. Push to Docker Hub

```bash
docker push your-username/mens-health-server:latest
```

## Versioned Releases

To push a specific version:

```bash
# Set version
export VERSION=v1.0.0

# Run the script
./push-to-dockerhub.sh
```

This will create and push both versioned and latest tags:

- `your-username/mens-health-server:v1.0.0`
- `your-username/mens-health-server:latest`

## Using the Published Image

Once pushed, others can use your image:

### Pull and Run

```bash
# Pull the image
docker pull your-username/mens-health-server:latest

# Run with environment file
docker run -p 8004:8004 --env-file .env your-username/mens-health-server:latest
```

### Docker Compose with Hub Image

Update your `docker-compose.yml` to use the Hub image instead of building locally:

```yaml
services:
  mens-health-api:
    image: your-username/mens-health-server:latest
    # Remove the 'build: .' line
    container_name: mens-health-api
    # ... rest of configuration
```

## Production Deployment

### Environment Variables for Production

Create a production `.env` file:

```bash
# Production MongoDB (consider MongoDB Atlas)
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/mens_health_db

# Strong JWT secret
SECRET_KEY=your-very-long-and-random-secret-key-for-production

# Production AWS SES credentials
AWS_ACCESS_KEY_ID=your-production-access-key
AWS_SECRET_ACCESS_KEY=your-production-secret-key
SENDER_EMAIL=noreply@yourdomain.com

# Production settings
DEVELOPMENT_MODE=false
LOG_LEVEL=info
```

### Deploy to Cloud Platforms

#### AWS ECS

```bash
# Create task definition using your Docker Hub image
aws ecs create-task-definition --cli-input-json file://task-definition.json
```

#### Google Cloud Run

```bash
gcloud run deploy mens-health-server \
  --image=your-username/mens-health-server:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name mens-health-server \
  --image your-username/mens-health-server:latest \
  --ports 8004
```

## Repository Settings

### Automated Builds

Set up automated builds on Docker Hub:

1. Go to [Docker Hub](https://hub.docker.com)
2. Create a new repository
3. Connect to your GitHub repository
4. Configure build rules:
   - Source: `main` branch
   - Tag: `latest`
   - Dockerfile location: `/`

### GitHub Actions

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Docker Publish

on:
  push:
    branches: [main]
    tags: ["v*"]

jobs:
  push_to_registry:
    name: Push Docker image to Docker Hub
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repo
        uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v3
        with:
          context: .
          push: true
          tags: your-username/mens-health-server:latest
```

## Security Best Practices

### Multi-arch Builds

Build for multiple architectures:

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -t your-username/mens-health-server:latest --push .
```

### Image Scanning

Scan for vulnerabilities:

```bash
docker scout quickview your-username/mens-health-server:latest
```

### Private Repository

For sensitive applications, consider using a private Docker Hub repository or alternative registries like:

- AWS ECR
- Google Container Registry
- Azure Container Registry

## Troubleshooting

### Authentication Issues

```bash
# Re-login if authentication fails
docker logout
docker login
```

### Build Failures

```bash
# Check Docker daemon
docker info

# Clean build cache
docker builder prune -a
```

### Push Failures

```bash
# Check available space
docker system df

# Clean up unused images
docker image prune -a
```

## Monitoring and Updates

### Image Updates

```bash
# Pull latest image
docker pull your-username/mens-health-server:latest

# Restart containers with new image
docker-compose down
docker-compose up -d
```

### Health Monitoring

The image includes health checks. Monitor with:

```bash
docker ps  # Shows health status
docker logs container-name  # View logs
```
