# Men's Health Agent Server

A FastAPI-based server that integrates with Google ADK agents to provide men's health, fitness, and wellness guidance through AI-powered conversations.

## Architecture

This server follows the agentic flow architecture pattern with:

- **FastAPI Server**: Standardized REST API with CORS support
- **TaskManager**: Orchestrates Google ADK agent interactions
- **Session Management**: Maintains conversation context across requests
- **Specialized Endpoints**: Domain-specific endpoints for health, fitness, and nutrition

## Features

- 🤖 **AI-Powered Conversations**: Uses Google ADK with LLM integration
- 🏥 **Health Assessments**: Specialized endpoint for health evaluations
- 💪 **Fitness Planning**: Custom fitness plan generation
- 🥗 **Nutrition Advice**: Personalized nutrition guidance
- 📊 **Session Management**: Maintains conversation context
- 🔄 **Auto-reload**: Development mode with hot reloading

## Quick Start

### 1. Setup Environment

```bash
# Clone or navigate to the project
cd men-server

# Make the startup script executable
chmod +x start_server.sh

# Run the startup script (creates venv, installs deps, starts server)
./start_server.sh
```

### 2. Manual Setup (Alternative)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (if you have a .env file)
export $(cat .env | xargs)

# Start the server
python main.py
```

### 3. Access the Server

- **Server**: http://localhost:8004
- **API Documentation**: http://localhost:8004/docs
- **Agent Metadata**: http://localhost:8004/.well-known/agent.json

## API Endpoints

### Core Endpoints

#### `POST /run`

Main agent interaction endpoint.

```json
{
  "message": "I need help with my health",
  "context": { "user_id": "user123" },
  "session_id": "optional-session-id"
}
```

#### `GET /health`

Health check endpoint.

```json
{
  "status": "healthy",
  "agent": "Men's Health Assistant",
  "version": "1.0.0"
}
```

### Specialized Endpoints

#### `POST /health_assessment`

Health assessment requests.

```json
{
  "message": "I'm 30 years old, 6ft, 180lbs. Assess my health.",
  "context": { "age": 30, "height": "6ft", "weight": "180lbs" },
  "session_id": "optional"
}
```

#### `POST /fitness_plan`

Fitness planning requests.

```json
{
  "message": "Create a muscle building workout plan",
  "context": { "goal": "muscle_building", "experience": "beginner" },
  "session_id": "optional"
}
```

#### `POST /nutrition_advice`

Nutrition guidance requests.

```json
{
  "message": "What should I eat to gain muscle?",
  "context": { "goal": "muscle_gain", "dietary_restrictions": [] },
  "session_id": "optional"
}
```

## Testing the Server

### Using the Test Client

```bash
# Run the test client
python test_client.py
```

### Using curl

```bash
# Health check
curl http://localhost:8004/health

# General chat
curl -X POST http://localhost:8004/run \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need health advice"}'

# Health assessment
curl -X POST http://localhost:8004/health_assessment \
  -H "Content-Type: application/json" \
  -d '{"message": "Assess my health for a 30-year-old male"}'
```

### Using httpx (Python)

```python
import httpx
import asyncio

async def test_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8004/run",
            json={"message": "I need fitness advice"}
        )
        print(response.json())

asyncio.run(test_agent())
```

## Project Structure

```
men-server/
├── chat_agent/           # Google ADK agent configuration
│   ├── __init__.py
│   └── agent.py         # Base agent definition
├── common/              # Shared utilities
│   └── server.py        # FastAPI server factory
├── agents/              # Agent management
│   └── task_manager.py  # TaskManager for agent orchestration
├── .well-known/         # Agent metadata (auto-generated)
│   └── agent.json
├── documentation/       # Architecture documentation
│   └── AGENTIC_FLOW.md
├── main.py             # Main server entry point
├── test_client.py      # Test client for API interaction
├── requirements.txt    # Python dependencies
├── start_server.sh     # Startup script
└── README.md          # This file
```

## Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
GOOGLE_API_KEY=your_google_api_key_here
PORT=8004
HOST=0.0.0.0
LOG_LEVEL=info
```

### Agent Configuration

The agent is configured in `chat_agent/agent.py`. You can modify:

- Model type (currently using OpenAI GPT-3)
- Agent instructions and personality
- Tools and capabilities

## Development

### Adding Custom Endpoints

1. Define your endpoint function:

```python
async def my_custom_endpoint(request: AgentRequest):
    # Add custom logic
    request.context["custom_field"] = "value"

    # Process through task manager
    task_manager = TaskManager(base_agent)
    result = await task_manager.process_task(
        request.message,
        request.context,
        request.session_id
    )

    return AgentResponse(
        message=result.get("message"),
        status=result.get("status", "success"),
        data=result.get("data", {}),
        session_id=request.session_id
    )
```

2. Add it to the custom_endpoints dict in `main.py`:

```python
custom_endpoints = {
    "my_custom_endpoint": my_custom_endpoint,
    # ... other endpoints
}
```

### Extending the Agent

To add more capabilities to the agent:

1. Create tools following the Google ADK pattern
2. Add them to the agent configuration
3. Update the agent instructions

## Deployment

### Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8004
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8004

CMD ["python", "main.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or support, please open an issue in the repository.
