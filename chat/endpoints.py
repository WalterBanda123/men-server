"""
Chat endpoints with WebSocket support and session management
"""
import logging
import json
import time
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from database.models import User, ChatSession, ChatMessage
from services.chat_service import chat_service
from services.auth_service import auth_service
from agents.task_manager import TaskManager
from chat_agent.agent import base_agent

logger = logging.getLogger(__name__)

# Create router
chat_router = APIRouter(prefix="/chat", tags=["Chat"])

# Security scheme
security = HTTPBearer()

# Initialize task manager
task_manager = TaskManager(base_agent)


async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from JWT token"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify token
        payload = auth_service.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception

        email = payload.get("email")
        if email is None:
            raise credentials_exception

        # Get user from database
        user = await auth_service.get_user_by_email(email)
        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception


# WebSocket endpoint for real-time chat
@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time chat

    Usage:
        ws://localhost:8004/chat/ws?token=<JWT_TOKEN>

    Message format (client -> server):
        {
            "message": "User's message",
            "session_id": "optional-session-id",
            "message_type": "chat"  // or health_assessment, fitness_plan, etc.
        }

    Response format (server -> client):
        {
            "type": "response",
            "message": "Bot's response",
            "session_id": "session-id",
            "user_id": "user-id",
            "timestamp": "2024-01-01T00:00:00",
            "data": {
                "raw_events": {...},
                "response_time_ms": 1234
            }
        }
    """
    await websocket.accept()

    # Authenticate user from token
    try:
        payload = auth_service.verify_token(token)
        if not payload:
            await websocket.send_json({"type": "error", "message": "Invalid token"})
            await websocket.close()
            return

        email = payload.get("email")
        user = await auth_service.get_user_by_email(email)

        if not user:
            await websocket.send_json({"type": "error", "message": "User not found"})
            await websocket.close()
            return

        user_id = str(user.id)
        logger.info(f"WebSocket connected for user: {email}")

        # Send connection success
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Men's Health Chat",
            "user_id": user_id
        })

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.send_json({"type": "error", "message": "Authentication failed"})
        await websocket.close()
        return

    # Message handling loop
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            message = data.get("message", "")
            session_id = data.get("session_id")
            message_type = data.get("message_type", "chat")

            if not message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Empty message"
                })
                continue

            # Start timing
            start_time = time.time()

            # Get or create session
            session = await chat_service.get_or_create_session(
                user_id=user_id,
                session_id=session_id
            )
            session_id = session.session_id

            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "session_id": session_id
            })

            # Process message through agent
            context = {
                "user_id": user_id,
                "message_type": message_type,
                "user_profile": {
                    "age": user.age,
                    "height": user.height,
                    "weight": user.weight,
                    "fitness_level": user.fitness_level,
                    "health_goals": user.health_goals
                }
            }

            result = await task_manager.process_task(
                message=message,
                context=context,
                session_id=session_id
            )

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Save message to database
            await chat_service.save_message(
                session_id=session_id,
                user_id=user_id,
                user_message=message,
                bot_response=result.get("message", ""),
                message_type=message_type,
                context=context,
                response_time_ms=response_time_ms,
                raw_events=result.get("data", {}).get("raw_events")
            )

            # Send response to client
            await websocket.send_json({
                "type": "response",
                "message": result.get("message", ""),
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": session.updated_at.isoformat() if session.updated_at else None,
                "data": {
                    "raw_events": result.get("data", {}).get("raw_events"),
                    "response_time_ms": response_time_ms,
                    "processing_method": result.get("data", {}).get("processing_method", "agent_llm")
                }
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {email}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            })
        except:
            pass


# REST API endpoints for session management

class SessionListResponse(BaseModel):
    sessions: list
    total: int


class SessionDetailResponse(BaseModel):
    session_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list


@chat_router.get("/sessions", response_model=SessionListResponse)
async def get_sessions(
    limit: int = 20,
    current_user: User = Depends(get_current_user_from_token)
):
    """Get all chat sessions for the current user"""
    try:
        sessions = await chat_service.get_user_sessions(
            user_id=str(current_user.id),
            limit=limit
        )

        session_list = [
            {
                "session_id": s.session_id,
                "title": s.title,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                "is_active": s.is_active
            }
            for s in sessions
        ]

        return SessionListResponse(
            sessions=session_list,
            total=len(session_list)
        )

    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sessions"
        )


@chat_router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user_from_token)
):
    """Get session details with message history"""
    try:
        # Get session
        session = await ChatSession.find_one(
            ChatSession.session_id == session_id,
            ChatSession.user_id == str(current_user.id)
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get messages
        messages = await chat_service.get_session_history(
            session_id=session_id,
            user_id=str(current_user.id),
            limit=100
        )

        message_list = [
            {
                "message": m.message,
                "response": m.response,
                "message_type": m.message_type,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "response_time_ms": m.response_time_ms
            }
            for m in messages
        ]

        return SessionDetailResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            title=session.title,
            created_at=session.created_at.isoformat() if session.created_at else "",
            updated_at=session.updated_at.isoformat() if session.updated_at else "",
            messages=message_list
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session details"
        )


@chat_router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user_from_token)
):
    """Delete a chat session"""
    try:
        success = await chat_service.delete_session(
            session_id=session_id,
            user_id=str(current_user.id)
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting session"
        )
