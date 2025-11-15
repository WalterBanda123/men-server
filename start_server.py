#!/usr/bin/env python3
"""
Startup script for Men's Health Server in production
Handles async initialization properly for Docker deployment
"""
import asyncio
import uvicorn
from main import create_mens_health_server


async def start_server():
    """Start the server with proper async initialization"""
    # Create the server
    app = await create_mens_health_server()
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Docker and load balancers"""
        return {
            "status": "healthy",
            "service": "Men's Health Server"
        }
    
    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
        access_log=True
    )
    
    # Start server
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    print("🚀 Starting Men's Health Server in production mode...")
    print("📖 API Documentation will be available at http://localhost:8004/docs")
    print("🔍 Health check at http://localhost:8004/health")
    
    asyncio.run(start_server())