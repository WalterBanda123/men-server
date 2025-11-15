# Men's Health App - API Endpoints Reference

## Base URL
```
Development: http://localhost:8004
Production: https://your-domain.com
```

---

## 🔐 Authentication Endpoints

### 1. Sign Up (Register New User)

**Endpoint:** `POST /auth/signup`

**Request Body:**
```json
{
  "email": "walterbanda98@gmail.com",
  "password": "SecurePass123!",
  "first_name": "Walter",
  "last_name": "Banda"
}
```

**Response (200 OK):**
```json
{
  "message": "Account created successfully. Please check your email for verification code.",
  "email_status": "sent"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Email already registered"
}
```

**Notes:**
- Password must be at least 8 characters
- Email must be valid format
- Verification code sent to email (or logged in dev mode)

---

### 2. Verify Email (After Signup)

**Endpoint:** `POST /auth/verify-email`

**Request Body:**
```json
{
  "email": "walterbanda98@gmail.com",
  "code": "123456"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "walterbanda98@gmail.com",
    "first_name": "Walter",
    "last_name": "Banda",
    "is_verified": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "age": null,
    "height": null,
    "weight": null,
    "fitness_level": null,
    "health_goals": []
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid or expired verification code"
}
```

**Notes:**
- Code expires in 15 minutes
- Returns JWT token on success
- Save `access_token` for authenticated requests

---

### 3. Sign In (Login)

**Endpoint:** `POST /auth/signin`

**Request Body:**
```json
{
  "email": "walterbanda98@gmail.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Please check your email for sign-in verification code.",
  "email_status": "sent"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid email or password"
}
```

**Notes:**
- Sends verification code to email
- Two-factor authentication via email

---

### 4. Verify Sign In (Complete Login)

**Endpoint:** `POST /auth/verify-signin`

**Request Body:**
```json
{
  "email": "walterbanda98@gmail.com",
  "code": "123456"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "walterbanda98@gmail.com",
    "first_name": "Walter",
    "last_name": "Banda",
    "is_verified": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "age": 30,
    "height": "6'0\"",
    "weight": "180 lbs",
    "fitness_level": "intermediate",
    "health_goals": ["muscle_gain", "endurance"]
  }
}
```

**Notes:**
- Returns JWT token on successful verification
- Token expires in 30 minutes (configurable)

---

### 5. Resend Verification Code

**Endpoint:** `POST /auth/resend-code`

**Request Body:**
```json
{
  "email": "walterbanda98@gmail.com",
  "code_type": "signup"
}
```

**Code Types:**
- `signup` - For email verification after signup
- `signin` - For login verification
- `password_reset` - For password reset

**Response (200 OK):**
```json
{
  "message": "Verification code sent to walterbanda98@gmail.com",
  "email_status": "sent"
}
```

---

### 6. Get Current User Profile

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "walterbanda98@gmail.com",
  "first_name": "Walter",
  "last_name": "Banda",
  "is_verified": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "age": 30,
  "height": "6'0\"",
  "weight": "180 lbs",
  "fitness_level": "intermediate",
  "health_goals": ["muscle_gain", "endurance"]
}
```

---

### 7. Verify Token

**Endpoint:** `GET /auth/verify-token`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "507f1f77bcf86cd799439011",
  "email": "walterbanda98@gmail.com",
  "is_verified": true
}
```

**Notes:**
- Use to check if token is still valid
- Returns 401 if token expired

---

## 💬 Chat & Conversation Endpoints

### 8. WebSocket Chat (Real-time)

**Endpoint:** `ws://localhost:8004/chat/ws?token=<JWT_TOKEN>`

**Protocol:** WebSocket

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8004/chat/ws?token=' + accessToken);
```

**Client → Server (Send Message):**
```json
{
  "message": "What exercises should I do for muscle building?",
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
  "message_type": "fitness_plan"
}
```

**Message Types:**
- `chat` - General conversation
- `health_assessment` - Health-related queries
- `fitness_plan` - Workout/fitness questions
- `nutrition_advice` - Diet/nutrition questions

**Server → Client (Connection Confirmed):**
```json
{
  "type": "connected",
  "message": "Connected to Men's Health Chat",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Server → Client (Typing Indicator):**
```json
{
  "type": "typing",
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f"
}
```

**Server → Client (Response):**
```json
{
  "type": "response",
  "message": "For muscle building, I recommend focusing on compound exercises...",
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
  "user_id": "507f1f77bcf86cd799439011",
  "timestamp": "2024-01-01T00:00:00",
  "data": {
    "raw_events": {
      "model_version": "gpt-4-0613",
      "content": {
        "parts": [
          {
            "text": "For muscle building, I recommend..."
          }
        ],
        "role": "model"
      },
      "usage_metadata": {
        "total_token_count": 67,
        "prompt_token_count": 58,
        "candidates_token_count": 9
      }
    },
    "response_time_ms": 1234,
    "processing_method": "agent_llm"
  }
}
```

**Server → Client (Error):**
```json
{
  "type": "error",
  "message": "Invalid token"
}
```

**Notes:**
- Token passed as query parameter
- If `session_id` not provided, new session created
- Messages automatically saved to database
- Connection stays open until closed

---

### 9. Get All User Sessions (Conversation List)

**Endpoint:** `GET /chat/sessions`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `limit` (optional, default: 20) - Number of sessions to return

**Request:**
```
GET /chat/sessions?limit=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (200 OK):**
```json
{
  "sessions": [
    {
      "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
      "title": "Muscle Building Tips",
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T01:00:00",
      "is_active": true
    },
    {
      "session_id": "a7b2c3d4-e5f6-4789-a012-b345c6789def",
      "title": "Nutrition for Gains",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T11:30:00",
      "is_active": true
    }
  ],
  "total": 2
}
```

**Notes:**
- Returns most recent sessions first
- Only returns active (non-deleted) sessions
- Use for displaying conversation list

---

### 10. Get Session Details with Messages

**Endpoint:** `GET /chat/sessions/{session_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```
GET /chat/sessions/365db837-bdd3-434e-bebb-4c7fdcc3c22f
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (200 OK):**
```json
{
  "session_id": "365db837-bdd3-434e-bebb-4c7fdcc3c22f",
  "user_id": "507f1f77bcf86cd799439011",
  "title": "Muscle Building Tips",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T01:00:00",
  "messages": [
    {
      "message": "What exercises should I do for muscle building?",
      "response": "For muscle building, I recommend focusing on compound exercises like squats, deadlifts, bench press, and pull-ups. These target multiple muscle groups and promote overall strength and mass gain.",
      "message_type": "fitness_plan",
      "created_at": "2024-01-01T00:00:00",
      "response_time_ms": 1234
    },
    {
      "message": "How many sets and reps?",
      "response": "For muscle building (hypertrophy), aim for 3-4 sets of 8-12 reps per exercise. This rep range is optimal for muscle growth. Rest 60-90 seconds between sets.",
      "message_type": "fitness_plan",
      "created_at": "2024-01-01T00:05:00",
      "response_time_ms": 987
    }
  ]
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

**Notes:**
- Returns up to 100 most recent messages
- Messages ordered chronologically
- Use for displaying full conversation history
- Can be used to restore chat UI

---

### 11. Delete Session

**Endpoint:** `DELETE /chat/sessions/{session_id}`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```
DELETE /chat/sessions/365db837-bdd3-434e-bebb-4c7fdcc3c22f
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (200 OK):**
```json
{
  "message": "Session deleted successfully"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Session not found"
}
```

**Notes:**
- Soft delete (marks session as inactive)
- Data not actually removed from database
- Session won't appear in session list

---

## 🏥 Health Check

### 12. Server Health Check

**Endpoint:** `GET /health`

**No authentication required**

**Response (200 OK):**
```json
{
  "status": "healthy",
  "agent": "Men's Health Chat Assistant",
  "version": "1.0.0"
}
```

---

## 📋 Complete Frontend Flow Examples

### Flow 1: New User Signup & First Chat

```javascript
// 1. Sign up
const signupResponse = await fetch('http://localhost:8004/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'walter@example.com',
    password: 'SecurePass123!',
    first_name: 'Walter',
    last_name: 'Banda'
  })
});
// Response: { message: "Check email for code", email_status: "sent" }

// 2. User receives code: 123456 (from email or dev logs)

// 3. Verify email
const verifyResponse = await fetch('http://localhost:8004/auth/verify-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'walter@example.com',
    code: '123456'
  })
});
const { access_token, user } = await verifyResponse.json();
// Save token: localStorage.setItem('token', access_token);

// 4. Connect to WebSocket
const ws = new WebSocket(`ws://localhost:8004/chat/ws?token=${access_token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'connected') {
    console.log('Connected!', data.user_id);

    // 5. Send first message
    ws.send(JSON.stringify({
      message: 'I want to build muscle, what should I do?',
      message_type: 'fitness_plan'
    }));
  }

  if (data.type === 'typing') {
    // Show typing indicator
    console.log('Bot is typing...');
  }

  if (data.type === 'response') {
    // Display bot response
    console.log('Bot:', data.message);
    console.log('Session ID:', data.session_id); // Save for later
  }
};
```

---

### Flow 2: Returning User Login & View Conversations

```javascript
// 1. Sign in
const signinResponse = await fetch('http://localhost:8004/auth/signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'walter@example.com',
    password: 'SecurePass123!'
  })
});
// Response: { message: "Check email for code" }

// 2. User receives code: 654321

// 3. Verify signin
const verifyResponse = await fetch('http://localhost:8004/auth/verify-signin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'walter@example.com',
    code: '654321'
  })
});
const { access_token } = await verifyResponse.json();

// 4. Get conversation list
const sessionsResponse = await fetch('http://localhost:8004/chat/sessions?limit=20', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
const { sessions } = await sessionsResponse.json();
// Display sessions in UI

// 5. User clicks on a conversation
const selectedSessionId = sessions[0].session_id;

// 6. Get conversation messages
const sessionResponse = await fetch(
  `http://localhost:8004/chat/sessions/${selectedSessionId}`,
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const sessionData = await sessionResponse.json();
// Display messages in chat UI

// 7. Connect WebSocket to continue conversation
const ws = new WebSocket(`ws://localhost:8004/chat/ws?token=${access_token}`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'connected') {
    // Send message in existing session
    ws.send(JSON.stringify({
      message: 'What about nutrition?',
      session_id: selectedSessionId, // Continue existing conversation
      message_type: 'nutrition_advice'
    }));
  }
};
```

---

### Flow 3: Display Conversation History (Without WebSocket)

```javascript
const token = localStorage.getItem('token');

// 1. Get all sessions
const sessionsResponse = await fetch('http://localhost:8004/chat/sessions', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { sessions, total } = await sessionsResponse.json();

// 2. Display session list
sessions.forEach(session => {
  console.log(`${session.title} - ${session.updated_at}`);
});

// 3. When user clicks on a session
const selectedSession = sessions[0];
const detailResponse = await fetch(
  `http://localhost:8004/chat/sessions/${selectedSession.session_id}`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
const conversationDetail = await detailResponse.json();

// 4. Display messages
conversationDetail.messages.forEach(msg => {
  console.log(`User: ${msg.message}`);
  console.log(`Bot: ${msg.response}`);
  console.log(`Time: ${msg.created_at}`);
  console.log('---');
});
```

---

## 🔑 Authentication Headers

All protected endpoints require:

```
Authorization: Bearer <access_token>
```

Example:
```javascript
fetch('http://localhost:8004/chat/sessions', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
  }
});
```

---

## ⚠️ Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server issue |

---

## 🔄 Token Expiration

- **Access Token Expires:** 30 minutes (1800 seconds)
- **Verification Code Expires:** 15 minutes

When token expires:
1. User gets 401 Unauthorized
2. Redirect to sign-in page
3. Sign in again to get new token

---

## 📱 Quick Reference

### Authentication Flow
```
POST /auth/signup
  ↓
POST /auth/verify-email
  ↓
(Save access_token)
```

### Chat Flow
```
WS /chat/ws?token=<token>
  ↓
Send: { message, session_id }
  ↓
Receive: { type: "response", message, session_id }
```

### View History
```
GET /chat/sessions
  ↓
(User selects session)
  ↓
GET /chat/sessions/{session_id}
  ↓
(Display messages)
```

---

## 🎯 Implementation Priority

### Phase 1 (MVP):
1. ✅ `POST /auth/signup`
2. ✅ `POST /auth/verify-email`
3. ✅ `POST /auth/signin`
4. ✅ `POST /auth/verify-signin`
5. ✅ `WS /chat/ws`
6. ✅ `GET /chat/sessions`
7. ✅ `GET /chat/sessions/{id}`

### Phase 2:
8. `DELETE /chat/sessions/{id}`
9. `POST /auth/resend-code`
10. `GET /auth/me`

---

**All endpoints are ready and tested!** 🚀 Use this as your API reference for frontend development.
