"""
Common server utilities for creating standardized FastAPI agents
Based on the agentic flow architecture documentation
"""
import os
import json
import uuid
from typing import Dict, Any, Optional, Callable
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Standard request model for agent communication"""
    message: str = Field(..., description="The message to process")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    session_id: Optional[str] = Field(None, description="Session identifier")


class AgentResponse(BaseModel):
    """Standard response model for agent communication"""
    message: str = Field(..., description="The response message")
    status: str = Field(default="success", description="Response status")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional response data")
    session_id: Optional[str] = Field(None, description="Session identifier")





def create_agent_server(
    name: str,
    description: str,
    task_manager: Any,
    endpoints: Optional[Dict[str, Callable]] = None,
    well_known_path: Optional[str] = None
) -> FastAPI:
    """
    Factory function to create standardized agent servers
    
    Args:
        name: Agent name
        description: Agent description
        task_manager: TaskManager instance for processing requests
        endpoints: Optional custom endpoints dict
        well_known_path: Path for .well-known metadata
        
    Returns:
        FastAPI app instance
    """
    app = FastAPI(title=f"{name} Agent", description=description)
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",     # React
            "http://localhost:5173",     # Vite
            "http://localhost:8100",     # Ionic
            "https://deve-01.web.app",   # Firebase
            "*"  # Development only
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Auto-generate .well-known/agent.json metadata
    os.makedirs(well_known_path or ".well-known", exist_ok=True)
    agent_json_path = os.path.join(well_known_path or ".well-known", "agent.json")
    
    if not os.path.exists(agent_json_path):
        agent_metadata = {
            "name": name,
            "description": description,
            "endpoints": ["run"] + list(endpoints.keys() if endpoints else []),
            "version": "1.0.0"
        }
        with open(agent_json_path, "w") as f:
            json.dump(agent_metadata, f, indent=2)
    
    # Main request endpoint
    @app.post("/run", response_model=AgentResponse)
    async def run(request: AgentRequest = Body(...)):
        try:
            result = await task_manager.process_task(
                request.message,
                request.context,
                request.session_id
            )
            return AgentResponse(
                message=result.get("message", "Task completed"),
                status="success",
                data=result.get("data", {}),
                session_id=request.session_id
            )
        except Exception as e:
            return AgentResponse(
                message=f"Error processing request: {str(e)}",
                status="error",
                data={"error_type": type(e).__name__},
                session_id=request.session_id
            )
    

    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "agent": name, "version": "1.0.0"}
    
    # Metadata endpoint
    @app.get("/.well-known/agent.json")
    async def get_metadata():
        try:
            with open(agent_json_path, "r") as f:
                return JSONResponse(content=json.load(f))
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Agent metadata not found")
    
    # Add custom endpoints
    if endpoints:
        for path, handler in endpoints.items():
            app.add_api_route(f"/{path}", handler, methods=["POST"])
    
    return app