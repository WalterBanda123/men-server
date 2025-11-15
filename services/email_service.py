"""
AWS SES Email Service for sending verification codes
"""
import boto3
import random
import string
import logging
from typing import Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError
from decouple import config

from database.models import VerificationCode

logger = logging.getLogger(__name__)


class EmailService:
    """AWS SES Email Service for verification codes"""
    
    def __init__(self):
        self.ses_client = None
        self.sender_email = config('SENDER_EMAIL', default='no-reply@menshealth.com')
        self.aws_region = config('AWS_REGION', default='us-east-1')
        self._initialize_ses()
    
    def _initialize_ses(self):
        """Initialize AWS SES client"""
        try:
            # Check if we're in development mode (skip SES)
            dev_mode = str(config('DEVELOPMENT_MODE', default='false')).lower() == 'true'
            if dev_mode:
                logger.info("Development mode enabled - SES disabled")
                self.ses_client = None
                return
            
            # AWS credentials should be set via environment variables:
            # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
            aws_access_key = config('AWS_ACCESS_KEY_ID', default=None)
            aws_secret_key = config('AWS_SECRET_ACCESS_KEY', default=None)
            
            if not aws_access_key or not aws_secret_key:
                logger.warning("AWS credentials not found. Email service will be disabled.")
                self.ses_client = None
                return
            
            self.ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            logger.info("AWS SES client initialized successfully")
        except NoCredentialsError:
            logger.warning("AWS credentials not found. Email service will be disabled.")
            self.ses_client = None
        except Exception as e:
            logger.error(f"Error initializing SES client: {e}")
            self.ses_client = None
    
    def _generate_verification_code(self, length: int = 6) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.digits, k=length))
    
    async def send_verification_email(
        self, 
        email: str, 
        code_type: str = "signup",
        user_name: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        Send verification email with code
        
        Args:
            email: Recipient email address
            code_type: Type of verification (signup, signin, password_reset)
            user_name: Optional user name for personalization
            
        Returns:
            Tuple of (success, message/error)
        """
        if not self.ses_client:
            # Development mode - generate code but don't send email
            dev_mode = str(config('DEVELOPMENT_MODE', default='false')).lower() == 'true'
            if dev_mode:
                logger.info("Development mode - generating verification code without sending email")
                
                # Generate and save verification code
                verification_code = self._generate_verification_code()
                expires_at = datetime.utcnow() + timedelta(minutes=15)
                
                # Remove existing codes
                await VerificationCode.find(
                    VerificationCode.email == email,
                    VerificationCode.code_type == code_type
                ).delete()
                
                # Save new code
                code_doc = VerificationCode(
                    email=email,
                    code=verification_code,
                    code_type=code_type,
                    expires_at=expires_at
                )
                await code_doc.save()
                
                logger.info(f"🔓 DEV MODE - Verification code for {email}: {verification_code}")
                return True, f"Development mode: verification code is {verification_code}"
            
            logger.error("SES client not available")
            return False, "Email service not available"
        
        try:
            # Generate verification code
            verification_code = self._generate_verification_code()
            
            # Save verification code to database
            expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes expiry
            
            # Remove any existing codes for this email and type
            await VerificationCode.find(
                VerificationCode.email == email,
                VerificationCode.code_type == code_type
            ).delete()
            
            # Create new verification code
            code_doc = VerificationCode(
                email=email,
                code=verification_code,
                code_type=code_type,
                expires_at=expires_at
            )
            await code_doc.save()
            
            # Prepare email content based on code type
            subject, html_body, text_body = self._get_email_content(
                code_type, verification_code, user_name
            )
            
            # Send email via SES
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'},
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logger.info(f"Verification email sent to {email}. MessageId: {response['MessageId']}")
            return True, "Verification email sent successfully"
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"SES ClientError: {error_code} - {error_message}")
            return False, f"Failed to send email: {error_message}"
        
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
            return False, f"Failed to send email: {str(e)}"
    
    def _get_email_content(
        self, 
        code_type: str, 
        code: str, 
        user_name: Optional[str] = None
    ) -> tuple[str, str, str]:
        """Get email content based on verification type"""
        
        name = user_name or "User"
        
        if code_type == "signup":
            subject = "Welcome to Men's Health - Verify Your Account"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c5aa0;">Welcome to Men's Health Assistant!</h2>
                    <p>Hi {name},</p>
                    <p>Thank you for signing up for Men's Health Assistant. To complete your registration, please verify your email address using the code below:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h3 style="color: #2c5aa0; font-size: 28px; letter-spacing: 3px; margin: 0;">{code}</h3>
                    </div>
                    
                    <p>This verification code will expire in 15 minutes.</p>
                    <p>If you didn't create an account with us, please ignore this email.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated message from Men's Health Assistant. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Welcome to Men's Health Assistant!
            
            Hi {name},
            
            Thank you for signing up. Please verify your email address using this code: {code}
            
            This code will expire in 15 minutes.
            
            If you didn't create an account with us, please ignore this email.
            """
        
        elif code_type == "signin":
            subject = "Men's Health - Sign In Verification"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c5aa0;">Sign In Verification</h2>
                    <p>Hi {name},</p>
                    <p>Someone is trying to sign in to your Men's Health Assistant account. If this was you, please use the verification code below:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h3 style="color: #2c5aa0; font-size: 28px; letter-spacing: 3px; margin: 0;">{code}</h3>
                    </div>
                    
                    <p>This verification code will expire in 15 minutes.</p>
                    <p><strong>If this wasn't you, please secure your account immediately.</strong></p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated message from Men's Health Assistant. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Sign In Verification - Men's Health Assistant
            
            Hi {name},
            
            Someone is trying to sign in to your account. If this was you, use this code: {code}
            
            This code will expire in 15 minutes.
            
            If this wasn't you, please secure your account immediately.
            """
        
        elif code_type == "password_reset":
            subject = "Men's Health - Password Reset"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c5aa0;">Password Reset Request</h2>
                    <p>Hi {name},</p>
                    <p>You requested to reset your password for Men's Health Assistant. Use the verification code below to proceed:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h3 style="color: #2c5aa0; font-size: 28px; letter-spacing: 3px; margin: 0;">{code}</h3>
                    </div>
                    
                    <p>This verification code will expire in 15 minutes.</p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                    
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated message from Men's Health Assistant. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            text_body = f"""
            Password Reset - Men's Health Assistant
            
            Hi {name},
            
            You requested to reset your password. Use this verification code: {code}
            
            This code will expire in 15 minutes.
            
            If you didn't request this, please ignore this email.
            """
        
        else:
            # Generic verification
            subject = "Men's Health - Verification Code"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c5aa0;">Verification Code</h2>
                    <p>Hi {name},</p>
                    <p>Your verification code is:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px;">
                        <h3 style="color: #2c5aa0; font-size: 28px; letter-spacing: 3px; margin: 0;">{code}</h3>
                    </div>
                    
                    <p>This code will expire in 15 minutes.</p>
                </div>
            </body>
            </html>
            """
            text_body = f"Your verification code is: {code}\n\nThis code will expire in 15 minutes."
        
        return subject, html_body, text_body
    
    async def verify_code(self, email: str, code: str, code_type: str) -> tuple[bool, str]:
        """
        Verify a verification code
        
        Args:
            email: User email
            code: Verification code to check
            code_type: Type of verification
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Find the verification code
            code_doc = await VerificationCode.find_one(
                VerificationCode.email == email,
                VerificationCode.code == code,
                VerificationCode.code_type == code_type,
                VerificationCode.is_used == False
            )
            
            if not code_doc:
                return False, "Invalid or expired verification code"
            
            # Check if code is expired
            if datetime.utcnow() > code_doc.expires_at:
                await code_doc.delete()
                return False, "Verification code has expired"
            
            # Mark code as used
            code_doc.is_used = True
            await code_doc.save()
            
            return True, "Code verified successfully"
            
        except Exception as e:
            logger.error(f"Error verifying code: {e}")
            return False, "Error verifying code"


# Global email service instance
email_service = EmailService()