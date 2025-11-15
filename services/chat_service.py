"""
Chat Service for managing sessions and messages
Handles conversation persistence in database
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from database.models import ChatSession, ChatMessage, User

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat sessions and messages"""

    async def get_or_create_session(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> ChatSession:
        """
        Get existing session or create a new one

        Args:
            user_id: User's database ID
            session_id: Optional session identifier
            title: Optional session title

        Returns:
            ChatSession instance
        """
        try:
            # If session_id provided, try to find it
            if session_id:
                session = await ChatSession.find_one(
                    ChatSession.session_id == session_id,
                    ChatSession.user_id == user_id
                )
                if session:
                    logger.info(f"Found existing session: {session_id}")
                    return session

            # Create new session
            new_session_id = session_id or str(uuid.uuid4())
            session = ChatSession(
                user_id=user_id,
                session_id=new_session_id,
                title=title or "New Conversation",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                is_active=True
            )
            await session.save()
            logger.info(f"Created new session: {new_session_id}")
            return session

        except Exception as e:
            logger.error(f"Error getting/creating session: {e}")
            raise

    async def save_message(
        self,
        session_id: str,
        user_id: str,
        user_message: str,
        bot_response: str,
        message_type: str = "chat",
        context: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[int] = None,
        raw_events: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Save user message and bot response as a conversation pair

        Args:
            session_id: Session identifier
            user_id: User's database ID
            user_message: User's input message
            bot_response: Bot's response
            message_type: Type of message (chat, health_assessment, etc.)
            context: Additional context data
            response_time_ms: Response time in milliseconds
            raw_events: Raw event data from agent

        Returns:
            ChatMessage instance with both message and response
        """
        try:
            # Create context with raw events
            message_context = context or {}
            if raw_events:
                message_context['raw_events'] = raw_events

            # Save message-response pair
            message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                message=user_message,
                response=bot_response,
                message_type=message_type,
                context=message_context,
                created_at=datetime.utcnow(),
                response_time_ms=response_time_ms
            )
            await message.save()

            # Update session timestamp
            session = await ChatSession.find_one(
                ChatSession.session_id == session_id
            )
            if session:
                session.updated_at = datetime.utcnow()

                # Auto-generate title from first message if needed
                if session.title == "New Conversation":
                    session.title = self._generate_title(user_message)

                await session.save()

            logger.info(f"Saved message pair to session {session_id}")
            return message

        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise

    async def get_session_history(
        self,
        session_id: str,
        user_id: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Get conversation history for a session

        Args:
            session_id: Session identifier
            user_id: User's database ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of ChatMessage instances
        """
        try:
            messages = await ChatMessage.find(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id
            ).sort("created_at").limit(limit).to_list()

            # Messages already in chronological order (oldest first)
            return messages

        except Exception as e:
            logger.error(f"Error getting session history: {e}")
            return []

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[ChatSession]:
        """
        Get all sessions for a user

        Args:
            user_id: User's database ID
            limit: Maximum number of sessions to retrieve

        Returns:
            List of ChatSession instances
        """
        try:
            sessions = await ChatSession.find(
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            ).sort("-updated_at").limit(limit).to_list()

            return sessions

        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    async def delete_session(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """
        Soft delete a session (mark as inactive)

        Args:
            session_id: Session identifier
            user_id: User's database ID

        Returns:
            True if successful
        """
        try:
            session = await ChatSession.find_one(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )

            if session:
                session.is_active = False
                await session.save()
                logger.info(f"Deleted session: {session_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    def _generate_title(self, first_message: str, max_length: int = 50) -> str:
        """Generate a title from the first message"""
        # Clean and truncate the message
        title = first_message.strip()
        if len(title) > max_length:
            title = title[:max_length] + "..."
        return title or "New Conversation"


# Global chat service instance
chat_service = ChatService()
