"""
Authentication endpoints for user registration and login
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database.models import (
    UserSignup, UserSignin, VerifyEmailRequest, 
    ResendCodeRequest, TokenResponse, UserResponse, User
)
from services.auth_service import auth_service
from services.email_service import email_service

logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
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


@auth_router.post("/signup", response_model=dict)
async def signup(user_data: UserSignup):
    """
    User signup endpoint
    Creates user account and sends verification email
    """
    try:
        # Create user account
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Send verification email
        success, message = await email_service.send_verification_email(
            email=user_data.email,
            code_type="signup",
            user_name=user_data.first_name
        )
        
        if not success:
            logger.warning(f"Failed to send verification email: {message}")
            # Don't fail the signup if email fails, just warn the user
            return {
                "message": "Account created successfully. Please check your email for verification code.",
                "email_status": "email_failed",
                "email_error": message
            }
        
        return {
            "message": "Account created successfully. Please check your email for verification code.",
            "email_status": "sent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )


@auth_router.post("/verify-email", response_model=TokenResponse)
async def verify_email(verify_data: VerifyEmailRequest):
    """
    Verify email with verification code
    Returns JWT token upon successful verification
    """
    try:
        # Verify the code
        success, message = await email_service.verify_code(
            email=verify_data.email,
            code=verify_data.code,
            code_type="signup"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Mark user as verified
        user_verified = await auth_service.verify_user_email(verify_data.email)
        if not user_verified:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get verified user
        user = await auth_service.get_user_by_email(verify_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        # Update last login
        await auth_service.update_last_login(str(user.id))
        
        return auth_service.create_token_response(user, access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during email verification"
        )


@auth_router.post("/signin", response_model=dict)
async def signin(signin_data: UserSignin):
    """
    User signin endpoint
    Sends verification code to email for secure login
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=signin_data.email,
            password=signin_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Send signin verification email
        success, message = await email_service.send_verification_email(
            email=signin_data.email,
            code_type="signin",
            user_name=user.first_name
        )
        
        if not success:
            logger.warning(f"Failed to send signin verification email: {message}")
            return {
                "message": "Please check your email for sign-in verification code.",
                "email_status": "email_failed",
                "email_error": message
            }
        
        return {
            "message": "Please check your email for sign-in verification code.",
            "email_status": "sent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signin"
        )


@auth_router.post("/verify-signin", response_model=TokenResponse)
async def verify_signin(verify_data: VerifyEmailRequest):
    """
    Verify signin with verification code
    Returns JWT token upon successful verification
    """
    try:
        # Verify the code
        success, message = await email_service.verify_code(
            email=verify_data.email,
            code=verify_data.code,
            code_type="signin"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Get user
        user = await auth_service.get_user_by_email(verify_data.email)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or account deactivated"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(data={"sub": user.email})
        
        # Update last login
        await auth_service.update_last_login(str(user.id))
        
        return auth_service.create_token_response(user, access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signin verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signin verification"
        )


@auth_router.post("/resend-code", response_model=dict)
async def resend_verification_code(resend_data: ResendCodeRequest):
    """
    Resend verification code to email
    """
    try:
        # Check if user exists
        user = await auth_service.get_user_by_email(resend_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Send verification email
        success, message = await email_service.send_verification_email(
            email=resend_data.email,
            code_type=resend_data.code_type,
            user_name=user.first_name
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send verification code: {message}"
            )
        
        return {
            "message": f"Verification code sent to {resend_data.email}",
            "email_status": "sent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resend code error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while resending verification code"
        )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile
    """
    return auth_service.user_to_response(current_user)


@auth_router.get("/verify-token", response_model=dict)
async def verify_token_endpoint(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "is_verified": current_user.is_verified
    }