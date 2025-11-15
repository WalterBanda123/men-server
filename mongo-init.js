// MongoDB initialization script
// This script creates the database and initial collections with proper indexes

db = db.getSiblingDB('mens_health_db');

// Create collections with indexes
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

db.createCollection('verification_codes');
db.verification_codes.createIndex({ "email": 1, "code_type": 1 });
db.verification_codes.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });
db.verification_codes.createIndex({ "created_at": -1 });

db.createCollection('invalidated_tokens');
db.invalidated_tokens.createIndex({ "token_id": 1 }, { unique: true });
db.invalidated_tokens.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

db.createCollection('chat_sessions');
db.chat_sessions.createIndex({ "user_id": 1 });
db.chat_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.chat_sessions.createIndex({ "created_at": -1 });

db.createCollection('chat_messages');
db.chat_messages.createIndex({ "session_id": 1 });
db.chat_messages.createIndex({ "user_id": 1 });
db.chat_messages.createIndex({ "created_at": -1 });
db.chat_messages.createIndex({ "message_type": 1 });

print('Database and collections initialized successfully');