"""
Authentication service for user management
"""
import jwt
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException, status
from decouple import config

from database.models import User, UserResponse, TokenResponse, InvalidatedToken, UserProfileUpdate

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = str(config('SECRET_KEY', default='your-secret-key-change-this-in-production'))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(config('ACCESS_TOKEN_EXPIRE_MINUTES', default='30'))


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash"""
        # Truncate password to 72 bytes for bcrypt compatibility
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        # Truncate password to 72 bytes for bcrypt compatibility
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with unique ID for blacklisting"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add unique token ID for blacklisting
        token_id = str(uuid.uuid4())
        to_encode.update({
            "exp": expire,
            "jti": token_id  # JWT ID claim
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token (now async to check blacklist)"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            token_id: str = payload.get("jti")
            
            if email is None or token_id is None:
                return None
            
            # Check if token is blacklisted
            invalidated = await InvalidatedToken.find_one(InvalidatedToken.token_id == token_id)
            if invalidated:
                return None
            
            return {
                "email": email, 
                "exp": payload.get("exp"), 
                "jti": token_id
            }
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = await User.find_one(User.email == email)
            if not user:
                return None
            
            if not AuthService.verify_password(password, user.password_hash):
                return None
            
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    @staticmethod
    async def create_user(email: str, password: str, first_name: str, last_name: str) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await User.find_one(User.email == email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create new user
            hashed_password = AuthService.get_password_hash(password)
            new_user = User(
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                is_verified=False,  # Will be verified via email
                is_active=True
            )
            
            await new_user.save()
            logger.info(f"New user created: {email}")
            return new_user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating user account"
            )
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return await User.find_one(User.email == email)
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            return await User.get(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    @staticmethod
    async def verify_user_email(email: str) -> bool:
        """Mark user's email as verified"""
        try:
            user = await User.find_one(User.email == email)
            if not user:
                return False
            
            user.is_verified = True
            user.updated_at = datetime.utcnow()
            await user.save()
            
            logger.info(f"User email verified: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying user email: {e}")
            return False
    
    @staticmethod
    async def update_last_login(user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            user = await User.get(user_id)
            if not user:
                return False
            
            user.last_login = datetime.utcnow()
            await user.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False
    
    @staticmethod
    def user_to_response(user: User) -> UserResponse:
        """Convert User model to UserResponse"""
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            age=user.age,
            height=user.height,
            weight=user.weight,
            fitness_level=user.fitness_level,
            health_goals=user.health_goals
        )
    
    @staticmethod
    def create_token_response(user: User, access_token: str) -> TokenResponse:
        """Create token response with user data"""
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            user=AuthService.user_to_response(user)
        )

    @staticmethod
    async def logout(token: str) -> bool:
        """Logout user by blacklisting the JWT token"""
        try:
            # Decode token to get claims
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            token_id = payload.get("jti")
            exp_timestamp = payload.get("exp")
            
            if not email or not token_id or not exp_timestamp:
                return False
            
            # Convert exp timestamp to datetime
            expires_at = datetime.fromtimestamp(exp_timestamp)
            
            # Add token to blacklist
            invalidated_token = InvalidatedToken(
                token_id=token_id,
                user_email=email,
                expires_at=expires_at
            )
            
            await invalidated_token.save()
            logger.info(f"Token blacklisted for user: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return False
    
    @staticmethod
    async def update_user_profile(user: User, profile_data: UserProfileUpdate) -> Optional[User]:
        """Update user profile information"""
        try:
            # Update only provided fields
            update_data = {}
            
            if profile_data.first_name is not None:
                update_data["first_name"] = profile_data.first_name
            if profile_data.last_name is not None:
                update_data["last_name"] = profile_data.last_name
            if profile_data.age is not None:
                update_data["age"] = profile_data.age
            if profile_data.height is not None:
                update_data["height"] = profile_data.height
            if profile_data.weight is not None:
                update_data["weight"] = profile_data.weight
            if profile_data.fitness_level is not None:
                update_data["fitness_level"] = profile_data.fitness_level
            if profile_data.health_goals is not None:
                update_data["health_goals"] = profile_data.health_goals
            
            if not update_data:
                return user  # No changes to make
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            # Update the user
            for field, value in update_data.items():
                setattr(user, field, value)
            
            await user.save()
            logger.info(f"User profile updated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return None
    
    @staticmethod
    async def change_password(user: User, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Verify current password
            if not AuthService.verify_password(current_password, user.password_hash):
                return False
            
            # Hash new password
            new_password_hash = AuthService.get_password_hash(new_password)
            
            # Update password
            user.password_hash = new_password_hash
            user.updated_at = datetime.utcnow()
            
            await user.save()
            logger.info(f"Password changed for user: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False


# Global auth service instance
auth_service = AuthService()