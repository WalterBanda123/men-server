"""
Men's Health Agent Server
FastAPI server that integrates with Google ADK agents for men's health assistance
"""
import os
import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi import Depends

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.server import create_agent_server, AgentRequest, AgentResponse
from agents.task_manager import TaskManager
from chat_agent.agent import base_agent
from database.connection import init_database, close_database
from auth.endpoints import auth_router, get_current_user
from database.models import User


async def create_mens_health_server():
    """Create and configure the men's health agent server"""
    
    # Initialize database connection
    await init_database()
    
    # Initialize the task manager with the base agent
    task_manager = TaskManager(base_agent)
    
    # Custom endpoints for men's health specific functionality
    custom_endpoints = {
        "health_assessment": health_assessment_endpoint,
        "fitness_plan": fitness_plan_endpoint,
        "nutrition_advice": nutrition_advice_endpoint
    }
    
    # Create the server using the factory function
    app = create_agent_server(
        name="Men's Health Chat Assistant",
        description="AI-powered chat assistant for men's health, fitness, and wellness guidance",
        task_manager=task_manager,
        endpoints=custom_endpoints,
        well_known_path=".well-known"
    )
    
    # Include authentication router
    app.include_router(auth_router)
    
    # Add database cleanup on shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_database()
    
    return app


async def health_assessment_endpoint(request: AgentRequest, current_user: User = Depends(get_current_user)):
    """Custom endpoint for health assessments (requires authentication)"""
    # Add health-specific context
    request.context["assessment_type"] = "health"
    request.context["domain"] = "mens_health"
    request.context["user_id"] = str(current_user.id)
    request.context["user_profile"] = {
        "age": current_user.age,
        "height": current_user.height,
        "weight": current_user.weight,
        "fitness_level": current_user.fitness_level,
        "health_goals": current_user.health_goals
    }
    
    # Process through the main task manager
    task_manager = TaskManager(base_agent)
    result = await task_manager.process_task(
        f"Health Assessment Request for {current_user.first_name}: {request.message}",
        request.context,
        request.session_id
    )
    
    return AgentResponse(
        message=result.get("message", "Health assessment completed"),
        status=result.get("status", "success"),
        data=result.get("data", {}),
        session_id=request.session_id
    )


async def fitness_plan_endpoint(request: AgentRequest, current_user: User = Depends(get_current_user)):
    """Custom endpoint for fitness planning (requires authentication)"""
    # Add fitness-specific context
    request.context["plan_type"] = "fitness"
    request.context["domain"] = "mens_health"
    request.context["user_id"] = str(current_user.id)
    request.context["user_profile"] = {
        "age": current_user.age,
        "height": current_user.height,
        "weight": current_user.weight,
        "fitness_level": current_user.fitness_level,
        "health_goals": current_user.health_goals
    }
    
    # Process through the main task manager
    task_manager = TaskManager(base_agent)
    result = await task_manager.process_task(
        f"Fitness Plan Request for {current_user.first_name}: {request.message}",
        request.context,
        request.session_id
    )
    
    return AgentResponse(
        message=result.get("message", "Fitness plan generated"),
        status=result.get("status", "success"),
        data=result.get("data", {}),
        session_id=request.session_id
    )


async def nutrition_advice_endpoint(request: AgentRequest, current_user: User = Depends(get_current_user)):
    """Custom endpoint for nutrition advice (requires authentication)"""
    # Add nutrition-specific context
    request.context["advice_type"] = "nutrition"
    request.context["domain"] = "mens_health"
    request.context["user_id"] = str(current_user.id)
    request.context["user_profile"] = {
        "age": current_user.age,
        "height": current_user.height,
        "weight": current_user.weight,
        "fitness_level": current_user.fitness_level,
        "health_goals": current_user.health_goals
    }
    
    # Process through the main task manager
    task_manager = TaskManager(base_agent)
    result = await task_manager.process_task(
        f"Nutrition Advice Request for {current_user.first_name}: {request.message}",
        request.context,
        request.session_id
    )
    
    return AgentResponse(
        message=result.get("message", "Nutrition advice provided"),
        status=result.get("status", "success"),
        data=result.get("data", {}),
        session_id=request.session_id
    )


# Create the FastAPI app
app = None

async def get_app():
    global app
    if app is None:
        app = await create_mens_health_server()
    return app


if __name__ == "__main__":
    # Development server
    async def main():
        server_app = await create_mens_health_server()
        config = uvicorn.Config(
            server_app,
            host="0.0.0.0",
            port=8004,  # Using port 8004 as shown in the documentation
            log_level="info",
            reload=True  # Enable auto-reload for development
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    # Run the server
    print("🚀 Starting Men's Health Agent Server on http://localhost:8004")
    print("📖 API Documentation available at http://localhost:8004/docs")
    print("🔍 Agent metadata at http://localhost:8004/.well-known/agent.json")
    
    asyncio.run(main())