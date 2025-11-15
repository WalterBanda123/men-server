# Men's Health Server - Docker Deployment

This guide explains how to build and run the Men's Health Server using Docker.

## Quick Start

### 1. Environment Setup

Copy the Docker environment template:
```bash
cp .env.docker .env
```

Edit `.env` with your actual configuration:
- Replace AWS credentials with your actual SES credentials
- Change the JWT secret key to a strong, random value
- Update the sender email to your verified SES email

### 2. Build and Run with Docker Compose

Start the entire stack (API + MongoDB):
```bash
docker-compose up --build
```

This will:
- Build the Men's Health API Docker image
- Start a MongoDB container with proper initialization
- Set up networking between services
- Expose the API on port 8004

### 3. Access the Application

- **API Documentation**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/health
- **Agent Metadata**: http://localhost:8004/.well-known/agent.json

## Manual Docker Build

### Build the Image

```bash
docker build -t mens-health-server .
```

### Run the Container

```bash
docker run -d \
  --name mens-health-api \
  -p 8004:8004 \
  --env-file .env \
  mens-health-server
```

## Production Deployment

### Environment Variables

The following environment variables are required:

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://user:pass@host:port/db` |
| `DATABASE_NAME` | Database name | `mens_health_db` |
| `SECRET_KEY` | JWT secret key | `your-256-bit-secret` |
| `AWS_ACCESS_KEY_ID` | AWS access key for SES | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for SES | `your-secret-key` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `SENDER_EMAIL` | Verified sender email | `noreply@yourdomain.com` |

### Security Considerations

1. **JWT Secret**: Use a strong, randomly generated secret key
2. **Database**: Use authentication for MongoDB in production
3. **TLS**: Enable HTTPS/TLS in production
4. **Firewall**: Restrict access to necessary ports only
5. **User**: The container runs as non-root user for security

### Health Monitoring

The container includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "service": "Men's Health Server"
}
```

Docker health checks run every 30 seconds with a 30-second timeout.

## Development

### Development Mode

For development with auto-reload:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Debug Mode

To run with debug logging:
```bash
docker run -e LOG_LEVEL=debug mens-health-server
```

### Email Verification Bypass

For testing without AWS SES:
```bash
docker run -e DEVELOPMENT_MODE=true mens-health-server
```

## Troubleshooting

### Container Logs

View API logs:
```bash
docker logs mens-health-api
```

View MongoDB logs:
```bash
docker logs mens-health-mongodb
```

### Database Connection Issues

1. Ensure MongoDB is running: `docker ps`
2. Check network connectivity: `docker network ls`
3. Verify connection string in environment variables

### Email Issues

1. Verify AWS credentials are correct
2. Check sender email is verified in AWS SES
3. Use `DEVELOPMENT_MODE=true` to bypass email verification

### Port Conflicts

If port 8004 is in use:
```bash
docker-compose down
# Edit docker-compose.yml to change port mapping
docker-compose up
```

## Docker Images

### Multi-stage Build

The Dockerfile uses a multi-stage approach for smaller production images:
- Base: Python 3.12 slim
- Dependencies cached separately for faster rebuilds
- Non-root user for security
- Health checks included

### Image Size Optimization

The image is optimized for production:
- Uses slim Python base image
- Removes build dependencies after installation
- Excludes development files via `.dockerignore`
- Runs as non-root user

## API Endpoints

Once running, the following endpoints are available:

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login  
- `POST /auth/verify-email` - Email verification
- `POST /auth/verify-signin` - Sign-in verification
- `GET /auth/me` - Get current user profile
- `PUT /auth/profile` - Update user profile
- `POST /auth/change-password` - Change password
- `POST /auth/logout` - User logout

### Chat
- `WS /chat/ws/{session_id}` - WebSocket chat
- `POST /chat/message` - Send chat message
- `GET /chat/conversations` - Get conversations
- `GET /chat/conversation/{session_id}` - Get specific conversation

### Health & Monitoring
- `GET /health` - Health check
- `GET /.well-known/agent.json` - Agent metadata

## Support

For issues or questions:
1. Check the logs: `docker logs mens-health-api`
2. Verify environment variables are set correctly
3. Ensure all required ports are available
4. Check MongoDB connectivity