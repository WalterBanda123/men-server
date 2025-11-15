"""
Database models for men's health application
"""
from datetime import datetime, timedelta
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from pymongo import IndexModel


class InvalidatedToken(Document):
    """Model to track invalidated/blacklisted JWT tokens"""
    
    token_id: str  # JWT 'jti' claim
    user_email: str
    invalidated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime  # When the original token would have expired
    
    class Settings:
        name = "invalidated_tokens"
        indexes = [
            IndexModel(["token_id"], unique=True),
            IndexModel(["expires_at"], expireAfterSeconds=0)  # Auto-delete expired entries
        ]


class User(Document):
    """User model for authentication and profile management"""
    
    email: EmailStr
    password_hash: str
    first_name: str
    last_name: str
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Profile information
    age: Optional[int] = None
    height: Optional[str] = None  # e.g., "6ft 2in" or "188cm"
    weight: Optional[str] = None  # e.g., "180lbs" or "82kg"
    fitness_level: Optional[str] = None  # beginner, intermediate, advanced
    health_goals: Optional[List[str]] = []  # weight_loss, muscle_gain, etc.
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("email", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]


class VerificationCode(Document):
    """Verification codes for email verification and password reset"""
    
    email: EmailStr
    code: str
    code_type: str  # "signup", "signin", "password_reset"
    expires_at: datetime
    is_used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    attempts: int = 0  # Track verification attempts
    
    class Settings:
        name = "verification_codes"
        indexes = [
            IndexModel([("email", 1), ("code_type", 1)]),
            IndexModel([("expires_at", 1)], expireAfterSeconds=0),  # Auto-delete expired codes
            IndexModel([("created_at", -1)]),
        ]


class ChatSession(Document):
    """Chat sessions for conversation history"""
    
    user_id: str  # Reference to User._id
    session_id: str
    title: Optional[str] = None  # Auto-generated or user-defined title
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Settings:
        name = "chat_sessions"
        indexes = [
            IndexModel([("user_id", 1)]),
            IndexModel([("session_id", 1)], unique=True),
            IndexModel([("created_at", -1)]),
        ]


class ChatMessage(Document):
    """Chat message pairs (user message + bot response)"""
    
    session_id: str  # Reference to ChatSession.session_id
    user_id: str  # Reference to User._id
    message: str  # User's message
    response: str  # Bot's response
    message_type: str = "chat"  # chat, health_assessment, fitness_plan, nutrition_advice
    context: Optional[dict] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: Optional[int] = None  # Response time in milliseconds
    
    class Settings:
        name = "chat_messages"
        indexes = [
            IndexModel([("session_id", 1)]),
            IndexModel([("user_id", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("message_type", 1)]),
        ]


# Pydantic models for API requests/responses
class UserSignup(BaseModel):
    """User signup request model"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)  # bcrypt limit
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)


class UserSignin(BaseModel):
    """User signin request model"""
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    """Email verification request model"""
    email: EmailStr
    code: str


class ResendCodeRequest(BaseModel):
    """Resend verification code request model"""
    email: EmailStr
    code_type: str = "signup"  # signup, signin, password_reset


class LogoutRequest(BaseModel):
    """Request model for logout"""
    # No fields needed - token comes from Authorization header
    pass


class UserProfileUpdate(BaseModel):
    """User profile update model"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    age: Optional[int] = Field(None, ge=13, le=120)  # Age between 13-120
    height: Optional[str] = Field(None, max_length=20)
    weight: Optional[str] = Field(None, max_length=20)
    fitness_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    health_goals: Optional[List[str]] = None


class ChangePasswordRequest(BaseModel):
    """Change password request model"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    """User response model (without sensitive data)"""
    id: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    age: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    fitness_level: Optional[str] = None
    health_goals: Optional[List[str]] = None


class TokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse