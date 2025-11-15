"""
Database configuration and connection management
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from decouple import config
import logging

from database.models import User, VerificationCode, ChatSession, ChatMessage

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and management"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect_database(self):
        """Initialize database connection and models"""
        try:
            # Get MongoDB connection string from environment
            mongodb_url = str(config(
                'MONGODB_URL', 
                default='mongodb://localhost:27017'
            ))
            database_name = str(config('DATABASE_NAME', default='mens_health_db'))
            
            logger.info(f"Connecting to MongoDB: {mongodb_url}")
            
            # Create motor client
            self.client = AsyncIOMotorClient(mongodb_url)
            self.database = self.client[database_name]
            
            # Test the connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Initialize Beanie with document models
            if self.database is not None:
                await init_beanie(
                    database=self.database,  # type: ignore
                    document_models=[
                        User,
                        VerificationCode, 
                        ChatSession,
                        ChatMessage
                    ]
                )
            
            logger.info("Database models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    async def close_database(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    async def get_database_stats(self):
        """Get database statistics"""
        try:
            if self.database is None:
                logger.error("Database not initialized")
                return None
                
            stats = await self.database.command("dbStats")
            collections = await self.database.list_collection_names()
            
            return {
                "database_name": self.database.name,
                "collections": collections,
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "objects": stats.get("objects", 0)
            }
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return None


# Global database manager instance
db_manager = DatabaseManager()


async def init_database():
    """Initialize database connection"""
    await db_manager.connect_database()


async def close_database():
    """Close database connection"""
    await db_manager.close_database()


async def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance"""
    return db_manager.database