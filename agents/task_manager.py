"""
Task Manager for orchestrating Google ADK agents
Based on the agentic flow architecture documentation
"""
import logging
import uuid
from typing import Dict, Any, Optional
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types as adk_types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages agent execution using Google ADK Runner
    Handles session management and request routing
    """
    
    def __init__(self, agent):
        logger.info(f"Initializing TaskManager for agent {agent.name}")
        self.agent = agent
        
        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        
        # Create the ADK runner
        self.runner = Runner(
            agent=self.agent,
            app_name="mens_health_agent",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
    
    async def process_task(
        self,
        message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user request through the agent system
        
        Args:
            message: User's input message
            context: Additional context (user_id, image_data, etc.)
            session_id: Optional session identifier
            
        Returns:
            Dict with message, status, and data
        """
        user_id = context.get("user_id", "default_mens_health_user")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")
        
        # Get or create session
        session = await self.session_service.get_session(
            app_name="mens_health_agent",
            user_id=user_id,
            session_id=session_id
        )
        
        if not session:
            session = await self.session_service.create_session(
                app_name="mens_health_agent",
                user_id=user_id,
                session_id=session_id,
                state={}
            )
            logger.info(f"Created new session: {session_id}")
        

        
        # Process chat requests with the Google ADK agent
        logger.info("💬 Processing chat request with men's health agent")
        
        enhanced_message = f"User ID: {user_id}\n\n{message}"
        request_content = adk_types.Content(
            role="user",
            parts=[adk_types.Part(text=enhanced_message)]
        )
        
        try:
            # Run agent asynchronously
            events = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )
            
            final_message = "(No response generated)"
            raw_events = []
            
            # Process agent response events
            async for event in events:
                event_data = event.model_dump(exclude_none=True)
                raw_events.append(event_data)
                
                # Extract final response from agent
                if event.is_final_response() and event.content and event.content.role == 'model':
                    if event.content and event.content.parts:
                        final_message = event.content.parts[0].text
                    logger.info(f"Final response: {final_message}")
            
            return {
                "message": final_message,
                "status": "success",
                "data": {
                    "raw_events": raw_events[-1] if raw_events else None,
                    "processing_method": "agent_llm",
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing task with agent: {str(e)}")
            return {
                "message": f"Error: {str(e)}",
                "status": "error",
                "data": {"session_id": session_id}
            }