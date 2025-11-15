"""
Task Manager for orchestrating agents
Mock implementation to replace Google ADK dependencies
"""
import logging
import uuid
from typing import Dict, Any, Optional

# Mock implementations to replace Google ADK
class MockSessionService:
    def __init__(self):
        self.sessions = {}

class MockArtifactService:
    def __init__(self):
        self.artifacts = {}

class MockRunner:
    def __init__(self, agent, app_name: str, session_service, artifact_service):
        self.agent = agent
        self.app_name = app_name
        self.session_service = session_service
        self.artifact_service = artifact_service

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
        
        # Initialize mock services
        self.session_service = MockSessionService()
        self.artifact_service = MockArtifactService()
        
        # Create the mock runner
        self.runner = MockRunner(
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
        Process a user request through the mock agent system
        
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
        
        # Store session in mock service
        self.session_service.sessions[session_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "messages": []
        }
        
        logger.info(f"💬 Processing message: {message}")
        
        try:
            # Mock response generation
            # In a real implementation, this would call an actual LLM
            response_message = self._generate_mock_response(message, context)
            
            # Store the conversation
            self.session_service.sessions[session_id]["messages"].append({
                "user": message,
                "assistant": response_message,
                "timestamp": uuid.uuid4().hex[:8]
            })
            
            return {
                "message": response_message,
                "status": "success",
                "data": {
                    "processing_method": "mock_agent",
                    "session_id": session_id,
                    "agent_name": self.agent.name
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "message": f"I apologize, but I encountered an error processing your request. Please try again.",
                "status": "error",
                "data": {"session_id": session_id}
            }
    
    def _generate_mock_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate a mock response based on the message content
        In a real implementation, this would use an actual LLM
        """
        message_lower = message.lower()
        
        # Men's health specific responses
        if any(word in message_lower for word in ["fitness", "workout", "exercise"]):
            return "Based on your fitness inquiry, I recommend starting with a balanced routine that includes both cardiovascular exercise and strength training. Would you like me to suggest a specific workout plan tailored to your fitness level?"
        
        elif any(word in message_lower for word in ["nutrition", "diet", "food", "eat"]):
            return "Nutrition is crucial for men's health. A balanced diet should include lean proteins, complex carbohydrates, healthy fats, and plenty of vegetables. What specific nutritional goals are you trying to achieve?"
        
        elif any(word in message_lower for word in ["health", "wellness", "checkup"]):
            return "Men's health encompasses physical, mental, and emotional well-being. Regular check-ups, preventive care, and healthy lifestyle choices are key. Is there a specific health concern you'd like to discuss?"
        
        elif any(word in message_lower for word in ["stress", "mental health", "anxiety"]):
            return "Mental health is just as important as physical health. Stress management techniques like meditation, regular exercise, and adequate sleep can help. If you're experiencing persistent stress or anxiety, consider speaking with a healthcare professional."
        
        else:
            return "Thank you for your question about men's health. I'm here to help with fitness, nutrition, wellness, and general health guidance. Could you provide more specific details about what you'd like to know?"