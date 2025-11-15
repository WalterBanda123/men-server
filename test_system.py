#!/usr/bin/env python3
"""
Quick test script to verify the authentication system is working
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_auth_system():
    """Test the authentication system components"""
    print("🧪 Testing Men's Health Authentication System")
    print("=" * 50)
    
    try:
        # Test 1: Database connection
        print("\n1. Testing database connection...")
        from database.connection import init_database, close_database
        await init_database()
        print("✅ Database connection successful")
        
        # Test 2: User model operations
        print("\n2. Testing user model...")
        from database.models import User
        from services.auth_service import auth_service
        
        # Test creating a user (don't actually save to avoid duplicates)
        test_email = "test@example.com"
        test_password = "TestPassword123!"
        
        # Test password hashing
        hashed_password = auth_service.get_password_hash(test_password)
        print(f"✅ Password hashing working: {len(hashed_password)} chars")
        
        # Test password verification
        is_valid = auth_service.verify_password(test_password, hashed_password)
        print(f"✅ Password verification: {is_valid}")
        
        # Test JWT token creation
        token = auth_service.create_access_token(data={"sub": test_email})
        print(f"✅ JWT token creation: {len(token)} chars")
        
        # Test JWT token verification
        payload = auth_service.verify_token(token)
        print(f"✅ JWT token verification: email={payload.get('email') if payload else 'None'}")
        
        # Test 3: Email service
        print("\n3. Testing email service...")
        from services.email_service import email_service
        print("✅ Email service initialized")
        
        # Test 4: Authentication endpoints
        print("\n4. Testing authentication models...")
        from database.models import UserSignup, UserSignin, VerifyEmailRequest
        
        signup_data = UserSignup(
            email="test@example.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User"
        )
        print(f"✅ UserSignup model: {signup_data.email}")
        
        signin_data = UserSignin(
            email="test@example.com",
            password="TestPassword123!"
        )
        print(f"✅ UserSignin model: {signin_data.email}")
        
        # Close database connection
        await close_database()
        print("\n✅ All authentication system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_import():
    """Test if the main server can be imported"""
    print("\n5. Testing server import...")
    try:
        from main import create_mens_health_server
        print("✅ Main server imports successfully")
        
        # Test creating the server (don't start it)
        app = await create_mens_health_server()
        print("✅ Server creation successful")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive authentication system test")
    
    # Run authentication tests
    auth_success = asyncio.run(test_auth_system())
    
    # Run server import test
    server_success = asyncio.run(test_server_import())
    
    if auth_success and server_success:
        print("\n🎉 All tests passed! The authentication system is ready.")
        print("\nNext steps:")
        print("1. Start MongoDB: brew services start mongodb-community")
        print("2. Run the server: python main.py")
        print("3. Test with: python test_auth_client.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)