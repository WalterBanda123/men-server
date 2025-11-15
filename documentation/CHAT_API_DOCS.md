# Chat API Documentation

## Overview

The Men's Health Chat API provides real-time WebSocket communication and session management with persistent storage in MongoDB.

## Features

- ✅ **WebSocket Support** - Real-time bidirectional communication
- ✅ **Session Management** - Persistent conversation sessions per user
- ✅ **Message Storage** - All messages stored in MongoDB
- ✅ **User Context** - Messages include user profile and health data
- ✅ **Authentication** - JWT-based authentication for all endpoints
- ✅ **Response Tracking** - Track response times and agent events

---

## WebSocket Endpoint

### Connect to WebSocket

**URL:** `ws://localhost:8004/chat/ws?token=<JWT_TOKEN>`

**Authentication:** JWT token as query parameter

### Connection Flow

1. **Connect** - Client connects with JWT token
2. **Connection Confirmation** - Server sends connection success message
3. **Message Exchange** - Client sends messages, server responds
4. **Session Persistence** - All messages saved to database

### Message Format (Client → Server)

```json
{
  "message": "Your message here",
  "session_id": "optional-session-id",  // If omitted, new session created
  "message_type": "chat"  // Options: chat, health_assessment, fitness_plan, nutrition_advice
}
```

### Response Format (Server → Client)

#### Typing Indicator
```json
{
  "type": "typing",
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f"
}
```

#### Actual Response
```json
{
  "type": "response",
  "message": "Bot's response message",
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
  "user_id": "507f1f77bcf86cd799439011",
  "timestamp": "2024-01-01T00:00:00",
  "data": {
    "raw_events": {
      "model_version": "gpt-4-0613",
      "content": {...},
      "usage_metadata": {
        "total_token_count": 67
      }
    },
    "response_time_ms": 1234,
    "processing_method": "agent_llm"
  }
}
```

#### Error Response
```json
{
  "type": "error",
  "message": "Error description"
}
```

---

## REST API Endpoints

### 1. Get User Sessions

**GET** `/chat/sessions`

Get all chat sessions for the authenticated user.

**Authentication:** Bearer token required

**Query Parameters:**
- `limit` (optional, default: 20) - Maximum number of sessions

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
      "title": "Fitness improvement conversation",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T01:00:00",
      "is_active": true
    }
  ],
  "total": 5
}
```

---

### 2. Get Session Details

**GET** `/chat/sessions/{session_id}`

Get detailed information about a specific session including all messages.

**Authentication:** Bearer token required

**Response:**
```json
{
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
  "user_id": "507f1f77bcf86cd799439011",
  "title": "Fitness improvement conversation",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T01:00:00",
  "messages": [
    {
      "message": "Hello! I want to improve my fitness.",
      "response": "Great! I'd be happy to help you improve your fitness...",
      "message_type": "chat",
      "created_at": "2024-01-01T00:00:00",
      "response_time_ms": 1234
    }
  ]
}
```

---

### 3. Delete Session

**DELETE** `/chat/sessions/{session_id}`

Soft delete a chat session (marks as inactive).

**Authentication:** Bearer token required

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

---

## Database Schema

### ChatSession Collection

```javascript
{
  "_id": ObjectId,
  "user_id": String,           // Reference to User._id
  "session_id": String,         // UUID for session
  "title": String,              // Session title (auto-generated or custom)
  "created_at": DateTime,
  "updated_at": DateTime,
  "is_active": Boolean
}
```

### ChatMessage Collection

```javascript
{
  "_id": ObjectId,
  "session_id": String,         // Reference to ChatSession.session_id
  "user_id": String,            // Reference to User._id
  "message": String,            // User's input message
  "response": String,           // Bot's response
  "message_type": String,       // chat, health_assessment, fitness_plan, nutrition_advice
  "context": {
    "user_profile": {...},
    "raw_events": {...}
  },
  "created_at": DateTime,
  "response_time_ms": Integer
}
```

---

## Usage Examples

### Python WebSocket Client

```python
import asyncio
import json
import websockets

async def chat():
    token = "your-jwt-token"
    url = f"ws://localhost:8004/chat/ws?token={token}"

    async with websockets.connect(url) as websocket:
        # Receive connection confirmation
        print(await websocket.recv())

        # Send message
        await websocket.send(json.dumps({
            "message": "What exercises should I do?",
            "message_type": "fitness_plan"
        }))

        # Receive typing indicator
        print(await websocket.recv())

        # Receive response
        response = json.loads(await websocket.recv())
        print(response['message'])

asyncio.run(chat())
```

### JavaScript WebSocket Client

```javascript
const token = 'your-jwt-token';
const ws = new WebSocket(`ws://localhost:8004/chat/ws?token=${token}`);

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);

  if (data.type === 'connected') {
    // Send first message
    ws.send(JSON.stringify({
      message: 'Hello! I need fitness advice.',
      message_type: 'chat'
    }));
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### cURL Examples (REST API)

```bash
# Get all sessions
curl -X GET http://localhost:8004/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get specific session
curl -X GET http://localhost:8004/chat/sessions/SESSION_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Delete session
curl -X DELETE http://localhost:8004/chat/sessions/SESSION_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Message Types

| Type | Description | Use Case |
|------|-------------|----------|
| `chat` | General conversation | Default chat messages |
| `health_assessment` | Health-related queries | Medical advice, symptoms |
| `fitness_plan` | Fitness planning | Workout routines, exercises |
| `nutrition_advice` | Nutrition guidance | Diet plans, meal suggestions |

---

## Error Handling

### Common Errors

1. **Authentication Failed**
   ```json
   {
     "type": "error",
     "message": "Invalid token"
   }
   ```

2. **Empty Message**
   ```json
   {
     "type": "error",
     "message": "Empty message"
   }
   ```

3. **Session Not Found** (REST API)
   ```json
   {
     "detail": "Session not found"
   }
   ```

---

## Testing

### 1. Get JWT Token

```bash
# Sign up
curl -X POST http://localhost:8004/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Verify email (use code from email/logs)
curl -X POST http://localhost:8004/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456"
  }'

# Copy the access_token from response
```

### 2. Test WebSocket

```bash
# Install websockets
pip install websockets

# Run test script
python test_chat_websocket.py
```

### 3. Test REST API

```bash
# Get sessions
curl -X GET http://localhost:8004/chat/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Performance Considerations

- **Response Time**: Typically 1-3 seconds depending on query complexity
- **Message Limit**: 100 messages per session in history endpoint
- **Session Limit**: 20 sessions per user in sessions list
- **WebSocket Timeout**: No timeout - connection stays open
- **Database**: All messages persisted immediately

---

## Security

- ✅ JWT-based authentication required for all endpoints
- ✅ User can only access their own sessions and messages
- ✅ Soft delete prevents data loss
- ✅ CORS configured for frontend integration

---

## Support

For issues or questions:
- Check server logs for detailed error messages
- Verify JWT token is valid and not expired
- Ensure database connection is active
- Check WebSocket connection status
