# Store Agents Architecture Documentation

> **Complete Guide to Multi-Agent System Architecture**
> A comprehensive blueprint for replicating this agent architecture in new projects

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Core Components](#core-components)
4. [Agent Types](#agent-types)
5. [Request/Response Models](#requestresponse-models)
6. [FastAPI Integration](#fastapi-integration)
7. [Complete Code Examples](#complete-code-examples)
8. [Deployment Guide](#deployment-guide)
9. [Best Practices](#best-practices)

---

## System Overview

This is a **hybrid multi-agent system** that combines Google ADK agents with custom FastAPI agents to create a comprehensive store management platform.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request (Chat/API)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Server (Port 8004)                      │
│              create_agent_server()                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  TaskManager                                 │
│          (Google ADK Runner Integration)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│             Main Coordinator Agent                           │
│              (Google ADK Agent)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       │                               │
┌──────▼──────────┐          ┌────────▼────────┐
│  ADK Sub-Agents │          │ FastAPI Agents  │
│  - Financial    │          │ - Transactions  │
│  - Greeting     │          │ - Misc Cash     │
│  - Advisory     │          │                 │
└─────────────────┘          └─────────────────┘
                │                     │
       ┌────────┴─────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│              Common Services Layer                           │
│  UserService | ProductService | FinancialService             │
│  FirebaseStorageService | VisionService                      │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                Firebase/Firestore Database                   │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Each agent handles specific domain logic
2. **Hybrid Architecture**: Combines LLM intelligence (ADK) with deterministic logic (FastAPI)
3. **Tool-Based Design**: Functions wrapped as tools for agent execution
4. **Service Layer**: Shared business logic across all agents
5. **Session Management**: Stateful conversations with context preservation

---

## Architecture Patterns

### 1. Two-Tier Agent System

#### Tier 1: Google ADK Agents
- Use Google's Agent Development Kit (ADK)
- LLM-powered decision making (Gemini 1.5 Flash)
- Natural language understanding
- Coordination and routing capabilities

#### Tier 2: FastAPI Agent Classes
- Direct Python classes with deterministic logic
- Fast, predictable responses
- Complex business operations (AutoML, image processing)
- No LLM overhead for simple tasks

### 2. Request Routing Pattern

```python
# Unified Chat Coordinator Pattern
message = "Sold 2 bread and 1 milk"
    ↓
keyword_matching(['sell', 'sold', 'transaction'])
    ↓
route_to_agent('product_transaction')
    ↓
ProductTransactionAgent.process_chat_transaction()
    ↓
return ChatResponse(message, agent_used, status, data)
```

### 3. Tool Wrapping Pattern

```python
# Business function → Tool → Agent
async def petty_cash_withdrawal(user_id, amount, purpose):
    # Business logic
    return result

# Wrapped as Google ADK Tool
petty_cash_tool = FunctionTool(
    func=petty_cash_withdrawal,
    name="petty_cash_withdrawal",
    description="Record petty cash withdrawals"
)

# Added to Agent
agent = Agent(
    model=llm,
    tools=[petty_cash_tool],
    ...
)
```

---

## Core Components

### 1. Server Factory (`common/server.py`)

Creates standardized FastAPI servers with automatic endpoint generation.

```python
# File: common/server.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    message: str = Field(..., description="The message to process")
    context: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(None)

class AgentResponse(BaseModel):
    message: str = Field(..., description="The response message")
    status: str = Field(default="success")
    data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(None)

def create_agent_server(
    name: str,
    description: str,
    task_manager: Any,
    endpoints: Optional[Dict[str, Callable]] = None,
    well_known_path: Optional[str] = None
) -> FastAPI:
    """
    Factory function to create standardized agent servers

    Args:
        name: Agent name
        description: Agent description
        task_manager: TaskManager instance for processing requests
        endpoints: Optional custom endpoints dict
        well_known_path: Path for .well-known metadata

    Returns:
        FastAPI app instance
    """
    app = FastAPI(title=f"{name} Agent", description=description)

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",     # React
            "http://localhost:5173",     # Vite
            "http://localhost:8100",     # Ionic
            "https://deve-01.web.app",   # Firebase
            "*"  # Development only
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Auto-generate .well-known/agent.json metadata
    os.makedirs(well_known_path or ".well-known", exist_ok=True)
    agent_json_path = os.path.join(well_known_path or ".well-known", "agent.json")

    if not os.path.exists(agent_json_path):
        agent_metadata = {
            "name": name,
            "description": description,
            "endpoints": ["run", "analyze_image"] + list(endpoints.keys() if endpoints else []),
            "version": "1.0.0"
        }
        with open(agent_json_path, "w") as f:
            json.dump(agent_metadata, f, indent=2)

    # Main request endpoint
    @app.post("/run", response_model=AgentResponse)
    async def run(request: AgentRequest = Body(...)):
        try:
            result = await task_manager.process_task(
                request.message,
                request.context,
                request.session_id
            )
            return AgentResponse(
                message=result.get("message", "Task completed"),
                status="success",
                data=result.get("data", {}),
                session_id=request.session_id
            )
        except Exception as e:
            return AgentResponse(
                message=f"Error processing request: {str(e)}",
                status="error",
                data={"error_type": type(e).__name__},
                session_id=request.session_id
            )

    # Image analysis endpoint
    @app.post("/analyze_image", response_model=AgentResponse)
    async def analyze_image(request: ImageAnalysisRequest = Body(...)):
        context = {
            "user_id": request.user_id,
            "image_data": request.image_data,
            "is_url": request.is_url
        }
        result = await task_manager.process_task(request.message, context, None)
        return AgentResponse(
            message=result.get("message", "Image analysis completed"),
            status=result.get("status", "success"),
            data=result.get("data", {}),
            session_id=None
        )

    # Metadata endpoint
    @app.get("/.well-known/agent.json")
    async def get_metadata():
        with open(agent_json_path, "r") as f:
            return JSONResponse(content=json.load(f))

    # Report serving endpoints
    @app.get("/reports/{filename}")
    async def serve_pdf(filename: str):
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        file_path = os.path.join(reports_dir, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")

        return FileResponse(
            path=file_path,
            media_type='application/pdf',
            filename=filename
        )

    # Add custom endpoints
    if endpoints:
        for path, handler in endpoints.items():
            app.add_api_route(f"/{path}", handler, methods=["POST"])

    return app
```

### 2. Task Manager (`agents/assistant/task_manager.py`)

Orchestrates Google ADK agents and handles request processing.

```python
# File: agents/assistant/task_manager.py
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types as adk_types

class TaskManager:
    """
    Manages agent execution using Google ADK Runner
    Handles session management and request routing
    """

    def __init__(self, agent: Agent):
        logger.info(f"Initializing TaskManager for agent {agent.name}")
        self.agent = agent

        # Initialize ADK services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()

        # Initialize vision processor for direct image analysis
        self.vision_processor = ProductVisionProcessor()

        # Create the ADK runner
        self.runner = Runner(
            agent=self.agent,
            app_name="store_agents",
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )

    async def process_task(
        self,
        message: str,
        context: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user request through the agent system

        Args:
            message: User's input message
            context: Additional context (user_id, image_data, etc.)
            session_id: Optional session identifier

        Returns:
            Dict with message, status, and data
        """
        user_id = context.get("user_id", "default_store_agents_user")

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        # Get or create session
        session = await self.session_service.get_session(
            app_name="store_agents",
            user_id=user_id,
            session_id=session_id
        )

        if not session:
            session = await self.session_service.create_session(
                app_name="store_agents",
                user_id=user_id,
                session_id=session_id,
                state={}
            )
            logger.info(f"Created new session: {session_id}")

        # FAST PATH: Check for image data and process directly
        if "image_data" in context:
            logger.info("🖼️ Image data detected - processing directly with vision API")

            try:
                image_data = context.get("image_data", "")
                is_url = context.get("is_url", False)

                if not image_data:
                    return {
                        "message": "Image data is required but not provided",
                        "status": "error",
                        "data": {}
                    }

                # Process image directly (bypass agent for speed)
                vision_result = await self.vision_processor.process_image(
                    image_data,
                    is_url
                )

                if vision_result.get("success"):
                    product_info = vision_result.get("product", {})

                    return {
                        "message": f"✅ Product identified: {product_info.get('title', 'Unknown')}",
                        "status": "success",
                        "data": {
                            "product": product_info,
                            "processing_method": "direct_vision_api"
                        }
                    }
                else:
                    return {
                        "message": f"Failed to analyze image: {vision_result.get('error')}",
                        "status": "error",
                        "data": {"error": vision_result.get("error")}
                    }

            except Exception as e:
                logger.error(f"❌ Error in direct image processing: {str(e)}")
                return {
                    "message": f"Image processing error: {str(e)}",
                    "status": "error",
                    "data": {"error": str(e)}
                }

        # AGENT PATH: For non-image requests, use the Google ADK agent
        logger.info("📝 Processing text-only request with agent")

        enhanced_message = f"User ID: {user_id}\n\n{message}"
        request_content = adk_types.Content(
            role="user",
            parts=[adk_types.Part(text=enhanced_message)]
        )

        try:
            # Run agent asynchronously
            events = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )

            final_message = "(No response generated)"
            raw_events = []

            # Process agent response events
            async for event in events:
                event_data = event.model_dump(exclude_none=True)
                raw_events.append(event_data)

                # Extract final response from agent
                if event.is_final_response() and event.content and event.content.role == 'model':
                    if event.content and event.content.parts:
                        final_message = event.content.parts[0].text
                    logger.info(f"Final response: {final_message}")

            return {
                "message": final_message,
                "status": "success",
                "data": {
                    "raw_events": raw_events[-1] if raw_events else None,
                    "processing_method": "agent_llm"
                }
            }

        except Exception as e:
            logger.error(f"Error processing task with agent: {str(e)}")
            return {
                "message": f"Error: {str(e)}",
                "status": "error",
                "data": {}
            }
```

---

## Agent Types

### Type 1: Google ADK Coordinator Agent

**Purpose**: Main decision-making hub that routes requests to specialized sub-agents.

```python
# File: agents/assistant/agent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

async def create_main_agent():
    """
    Creates the main coordinator agent with specialized sub-agents
    """
    llm = LiteLlm(
        model="gemini/gemini-1.5-flash-latest",
        api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # Create all specialized sub-agents
    financial_reporting_agent = await create_financial_reporting_subagent()
    product_management_agent = await create_product_management_subagent()
    user_greeting_agent = await create_user_greeting_subagent()
    business_advisory_agent = await create_business_advisory_subagent()

    # Create the coordinator
    coordinator = Agent(
        model=llm,
        name='store_assistant_coordinator',
        description='Smart Business Assistant coordinator for informal traders',
        tools=[],  # No direct tools - delegates to sub-agents
        sub_agents=[
            financial_reporting_agent,
            product_management_agent,
            user_greeting_agent,
            business_advisory_agent
        ],
        instruction=(
            "You are the Smart Business Assistant Coordinator.\n\n"

            "🤖 YOUR ROLE AS COORDINATOR:\n"
            "- Analyze incoming requests and route to appropriate specialist\n"
            "- Ensure seamless collaboration between sub-agents\n"
            "- Provide unified, coherent responses\n"
            "- Maintain context across sub-agent interactions\n\n"

            "👥 YOUR SPECIALIZED TEAM:\n"
            "- Financial Reporting Agent: PDF reports and analytics\n"
            "- Product Management Agent: Inventory operations\n"
            "- User Greeting Agent: Personalization and onboarding\n"
            "- Business Advisory Agent: Strategic guidance\n\n"

            "⚡ DELEGATION STRATEGY:\n"
            "- Greetings → User Greeting Agent\n"
            "- Explicit report requests → Financial Reporting Agent\n"
            "- Product/inventory queries → Product Management Agent\n"
            "- Business advice → Business Advisory Agent\n"
            "- Complex requests → Coordinate multiple agents\n\n"

            "Always provide the best support by leveraging specialist expertise."
        )
    )

    return coordinator
```

### Type 2: Google ADK Sub-Agent (Specialized)

**Purpose**: Domain-specific agent with focused capabilities and tools.

```python
# File: agents/assistant/financial_reporting_subagent.py
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

async def create_financial_reporting_subagent():
    """
    Specialized sub-agent for financial reporting and PDF generation
    """
    llm = LiteLlm(
        model="gemini/gemini-1.5-flash-latest",
        api_key=os.environ.get("GOOGLE_API_KEY")
    )

    # Initialize services
    financial_service = FinancialService()
    user_service = UserService()

    # Create tool for report generation
    financial_report_tool = create_financial_report_tool(
        financial_service,
        user_service
    )

    agent = Agent(
        model=llm,
        name='financial_reporting_agent',
        description='Specialized agent for generating financial reports',
        tools=[financial_report_tool],
        instruction=(
            "You are a Financial Reporting Specialist.\n\n"

            "🎯 YOUR SPECIALIZATION:\n"
            "- Generate comprehensive PDF financial reports\n"
            "- Analyze business performance and provide insights\n"
            "- Create profit & loss statements\n"
            "- Provide trend analysis and recommendations\n\n"

            "🚨 IMPORTANT - WHEN TO GENERATE REPORTS:\n"
            "ONLY generate PDF reports when explicitly requested:\n"
            "- 'Generate a report', 'Create a report'\n"
            "- 'Financial report', 'PDF report'\n\n"

            "🚫 DO NOT GENERATE REPORTS FOR:\n"
            "- General questions about business performance\n"
            "- Casual inquiries without report request\n\n"

            "📊 REPORT GENERATION PROCESS:\n"
            "1. Ask for time period if not provided\n"
            "2. Use generate_financial_report tool\n"
            "3. Provide download link and key metrics\n"
            "4. Summarize insights\n\n"

            "Always be encouraging and provide actionable recommendations."
        )
    )

    return agent
```

### Type 3: FastAPI Agent Class

**Purpose**: Deterministic business logic without LLM overhead.

```python
# File: agents/product_transaction_agent/agent.py
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel

class ProductTransactionAgent:
    """
    Agent for handling product registration and transactions
    Direct Python class with deterministic logic
    """

    def __init__(self):
        self.name = "Product Transaction Agent"
        self.description = "Handles image-based product registration and chat transactions"
        self.helper = ProductTransactionHelper()

    async def register_product_image(
        self,
        request: ProductRegistrationRequest
    ) -> ProductRegistrationResponse:
        """
        Register a product via image using AutoML Vision

        Process:
        1. Preprocess image (decode base64 or fetch URL)
        2. Call AutoML model for prediction
        3. Look up product metadata by predicted SKU
        4. Upload image to Google Cloud Storage
        5. Return structured response
        """
        start_time = time.time()

        try:
            logger.info(f"Processing product registration for user: {request.user_id}")

            # Step 1: Preprocess image
            image_bytes = await self.helper.preprocess_image(
                request.image_data,
                request.is_url
            )
            if not image_bytes:
                raise HTTPException(status_code=400, detail="Invalid image data")

            # Step 2: Call AutoML model
            prediction_result = await self.helper.call_automl_model(
                image_bytes,
                request.user_id
            )

            if not prediction_result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to analyze image")

            # Step 3: Look up product metadata
            product_metadata = None
            if prediction_result.get("sku"):
                product_metadata = await self.helper.lookup_product_by_sku(
                    prediction_result["sku"],
                    request.user_id
                )

            # Step 4: Upload to GCS
            image_url = None
            if request.enhance_image:
                image_url = await self.helper.upload_to_gcs(
                    image_bytes,
                    request.user_id
                )

            # Step 5: Build response
            processing_time = time.time() - start_time

            product_data = {
                "title": prediction_result.get("title", "Unknown Product"),
                "brand": prediction_result.get("brand", ""),
                "category": prediction_result.get("category", "General"),
                "size": prediction_result.get("size", ""),
                "unit": prediction_result.get("unit", ""),
            }

            if product_metadata:
                product_data.update(product_metadata)

            return ProductRegistrationResponse(
                success=True,
                message=f"Product registered: {product_data['title']}",
                product=product_data,
                confidence=prediction_result.get("confidence", 0.0),
                image_url=image_url,
                sku=prediction_result.get("sku"),
                processing_time=processing_time,
                detection_method="automl"
            )

        except Exception as e:
            logger.error(f"Error in product registration: {e}")
            return ProductRegistrationResponse(
                success=False,
                message=f"Product registration failed: {str(e)}",
                processing_time=time.time() - start_time
            )

    async def process_chat_transaction(
        self,
        request: TransactionRequest
    ) -> TransactionResponse:
        """
        Process a chat-based transaction

        Process:
        1. Check if message is stock inquiry or transaction
        2. Parse free-form transaction text (e.g., "2 bread @1.50, 1 milk")
        3. Look up products and validate stock
        4. Compute receipt with tax
        5. Save as pending (require confirmation)
        6. Return formatted confirmation request
        """
        try:
            logger.info(f"Processing: {request.message}")

            # Check for stock inquiry
            if self.helper.is_stock_inquiry(request.message):
                stock_result = await self.helper.handle_stock_inquiry(
                    request.message,
                    request.user_id
                )
                return TransactionResponse(
                    success=stock_result.get("success", True),
                    message=stock_result.get("message"),
                    chat_response=stock_result.get("message"),
                    confirmation_required=False
                )

            # Parse transaction message
            parsed_result = await self.helper.parse_cart_message(request.message)

            if not parsed_result.get("success"):
                return TransactionResponse(
                    success=False,
                    message="Could not understand transaction",
                    errors=[parsed_result.get("error", "Parse error")],
                    chat_response="Please use format: '2 bread, 1 milk' or '2 bread @1.50'"
                )

            items = parsed_result.get("items", [])
            if not items:
                return TransactionResponse(
                    success=False,
                    message="No products found",
                    errors=["No products identified"],
                    chat_response="Try: '2 bread, 1 milk'"
                )

            # Compute receipt
            receipt_result = await self.helper.compute_receipt(
                items,
                request.user_id,
                request.customer_name or "Walk-in Customer"
            )

            if not receipt_result.get("success"):
                return TransactionResponse(
                    success=False,
                    message="Transaction failed",
                    errors=receipt_result.get("errors", []),
                    warnings=receipt_result.get("warnings", [])
                )

            # Save as pending (two-step confirmation)
            receipt_data = receipt_result["receipt"]
            await self.helper.save_pending_transaction(receipt_data)

            # Format confirmation request
            confirmation_message = self.helper.format_confirmation_request(receipt_data)

            return TransactionResponse(
                success=True,
                message="Transaction registered - awaiting confirmation",
                receipt=Receipt(**receipt_data),
                chat_response=confirmation_message,
                pending_transaction_id=receipt_data['transaction_id'],
                confirmation_required=True
            )

        except Exception as e:
            logger.error(f"Error processing transaction: {e}")
            return TransactionResponse(
                success=False,
                message=f"Transaction failed: {str(e)}",
                errors=[str(e)]
            )
```

### Type 4: Unified Chat Coordinator

**Purpose**: Single endpoint that routes to all sub-agents intelligently.

```python
# File: unified_chat_agent.py
from fastapi import FastAPI, Body
from pydantic import BaseModel

class UnifiedChatCoordinator:
    """
    Main coordinator that routes chat requests to appropriate sub-agents
    """

    def __init__(self):
        self.name = "Store Assistant"
        self.description = "Unified chat interface for store management"

        # Initialize sub-agents
        self.product_agent = ProductTransactionAgent()
        self.misc_agent = MiscTransactionsAgent()

        # Initialize services
        self.user_service = UserService()
        self.product_service = RealProductService()

        # Agent capabilities with keywords
        self.agent_capabilities = {
            'product_transaction': {
                'agent': self.product_agent,
                'description': 'Handles sales, transactions, receipts',
                'keywords': ['sell', 'sold', 'buy', 'transaction', 'receipt']
            },
            'misc_transactions': {
                'agent': self.misc_agent,
                'description': 'Handles petty cash, drawings, deposits',
                'keywords': ['petty cash', 'drawing', 'deposit', 'withdraw']
            }
        }

    def should_route_to_agent(
        self,
        message: str,
        agent_type: str,
        has_image: bool = False
    ) -> bool:
        """
        Determine if message should go to specific agent based on keywords
        """
        message_lower = message.lower()

        if agent_type == 'product_transaction':
            if has_image:
                return True
            keywords = self.agent_capabilities['product_transaction']['keywords']
            return any(keyword in message_lower for keyword in keywords)

        elif agent_type == 'misc_transactions':
            keywords = self.agent_capabilities['misc_transactions']['keywords']
            return any(keyword in message_lower for keyword in keywords)

        return False

    async def route_to_agent(
        self,
        message: str,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Intelligent agent routing based on message content
        """
        try:
            has_image = bool(context.get('image_data'))
            message_lower = message.lower()

            # Handle greetings
            if any(g in message_lower for g in ['hello', 'hi', 'hey']):
                return await self.handle_general_help(message, user_id, context)

            # Handle reports (highest priority)
            if 'report' in message_lower:
                return await self.handle_financial_report(message, user_id, context)

            # Handle inventory queries
            if any(k in message_lower for k in ['inventory', 'stock', 'low stock']):
                return await self.handle_inventory_query(message, user_id, context)

            # Route to misc transactions
            if self.should_route_to_agent(message, 'misc_transactions'):
                return await self.handle_misc_transaction('auto', message, user_id, context)

            # Route to product transactions
            if self.should_route_to_agent(message, 'product_transaction', has_image):
                if has_image:
                    return await self.handle_product_registration(message, user_id, context)
                else:
                    return await self.handle_transaction(message, user_id, context)

            # Default to general help
            return await self.handle_general_help(message, user_id, context)

        except Exception as e:
            logger.error(f"Error routing: {e}")
            return {
                "message": f"Sorry, error: {str(e)}",
                "agent_used": "error_handler",
                "status": "error"
            }

    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Main chat processing function
        """
        user_id = request.user_id or request.context.get('user_id')
        if not user_id:
            return ChatResponse(
                message="❌ User ID required",
                agent_used="error_handler",
                status="error"
            )

        # Prepare context
        context = dict(request.context)
        if request.image_data:
            context['image_data'] = request.image_data
            context['is_url'] = request.is_url

        # Route to appropriate agent
        result = await self.route_to_agent(request.message, user_id, context)

        return ChatResponse(
            message=result["message"],
            agent_used=result["agent_used"],
            status=result["status"],
            data=result.get("data", {}),
            session_id=request.session_id
        )

# Create FastAPI app
app = FastAPI(title="Store Assistant")

# Add CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# Initialize coordinator
coordinator = UnifiedChatCoordinator()

@app.post("/run", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest = Body(...)):
    """Unified chat endpoint"""
    return await coordinator.process_chat(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Store Assistant"}
```

---

## Request/Response Models

### Core Models

```python
# File: common/server.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class AgentRequest(BaseModel):
    """Standard request model for all agents"""
    message: str = Field(..., description="The message to process")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (user_id, session_id, etc.)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for stateful interactions"
    )

class AgentResponse(BaseModel):
    """Standard response model for all agents"""
    message: str = Field(..., description="The response message")
    status: str = Field(
        default="success",
        description="Status: success, error, info"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional data (receipts, products, etc.)"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier"
    )

class ImageAnalysisRequest(BaseModel):
    """Request model for image-based operations"""
    message: str = Field(..., description="Processing instruction")
    image_data: str = Field(..., description="Base64 encoded image or URL")
    is_url: bool = Field(default=False, description="True if image_data is URL")
    user_id: str = Field(default="default_user", description="User identifier")
```

### Specialized Models for Product Transactions

```python
# File: agents/product_transaction_agent/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# =====================
# Product Registration Models
# =====================

class ProductRegistrationRequest(BaseModel):
    """Request for product registration via image"""
    image_data: str = Field(..., description="Base64 image or URL")
    user_id: str = Field(..., description="Store owner ID")
    is_url: bool = Field(default=False, description="Is image_data a URL?")
    enhance_image: Optional[bool] = Field(
        default=True,
        description="Upload to GCS?"
    )

class ProductRegistrationResponse(BaseModel):
    """Response from product registration"""
    success: bool
    message: str
    product: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None  # AutoML confidence
    image_url: Optional[str] = None     # GCS URL
    sku: Optional[str] = None           # Product SKU
    processing_time: Optional[float] = None
    detection_method: Optional[str] = None  # "automl" or "vision"

# =====================
# Transaction Models
# =====================

class LineItem(BaseModel):
    """Individual item in a transaction"""
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., description="Quantity purchased")
    unit_price: float = Field(..., description="Price per unit")
    line_total: float = Field(..., description="quantity * unit_price")
    sku: Optional[str] = Field(None, description="Product SKU")
    category: Optional[str] = Field(None, description="Product category")

class TransactionRequest(BaseModel):
    """Request for processing a transaction"""
    message: str = Field(
        ...,
        description="Free-form: '2 bread @1.5, 1 milk @0.75'"
    )
    user_id: str = Field(..., description="Store owner ID")
    customer_name: Optional[str] = Field(None, description="Customer name")
    payment_method: Optional[str] = Field(default="cash")

class Receipt(BaseModel):
    """Transaction receipt"""
    transaction_id: str
    user_id: str
    store_id: str
    customer_name: Optional[str] = None
    date: str
    time: str
    items: List[LineItem]
    subtotal: float
    tax_rate: float = Field(default=0.05, description="5% tax")
    tax_amount: float
    total: float
    payment_method: str = Field(default="cash")
    change_due: Optional[float] = None
    created_at: datetime
    status: str = Field(
        default="pending",
        description="pending, confirmed, cancelled"
    )

class TransactionResponse(BaseModel):
    """Response from transaction processing"""
    success: bool
    message: str
    receipt: Optional[Receipt] = None
    chat_response: Optional[str] = None  # Formatted for chat UI
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    confirmation_required: bool = Field(default=False)
    pending_transaction_id: Optional[str] = Field(
        None,
        description="ID for pending confirmation"
    )
```

### Chat Models for Unified Interface

```python
# File: unified_chat_agent.py
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Unified chat request"""
    message: str = Field(..., description="User's chat message")
    user_id: Optional[str] = Field(None, description="Can be in context")
    session_id: Optional[str] = Field(None)
    context: Dict[str, Any] = Field(default_factory=dict)
    image_data: Optional[str] = Field(None, description="Base64 image")
    is_url: Optional[bool] = Field(False)

class ChatResponse(BaseModel):
    """Unified chat response"""
    message: str = Field(..., description="Agent's response")
    agent_used: str = Field(..., description="Which agent handled this")
    status: str = Field(default="success", description="success/error/info")
    data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = Field(None)
```

---

## FastAPI Integration

### Entry Point Pattern

```python
# File: agents/assistant/__main__.py
import asyncio
import uvicorn
from dotenv import load_dotenv

from .task_manager import TaskManager
from .agent import root_agent
from common.server import create_agent_server

async def main():
    """Main entry point for agent server"""

    # Create agent instance
    agent_instance, exit_stack = await root_agent()

    async with exit_stack:
        # Create task manager
        task_manager_instance = TaskManager(agent=agent_instance)
        logger.info("TaskManager initialized")

        # Get server configuration
        host = os.getenv("STORE_AGENTS_HOST", "127.0.0.1")
        port = int(os.getenv("STORE_AGENTS_PORT", 8004))

        # Create FastAPI server using factory
        app = create_agent_server(
            name=agent_instance.name,
            description=agent_instance.description,
            task_manager=task_manager_instance
        )

        logger.info(f"Starting server on {host}:{port}")

        # Configure and run server
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        sys.exit(1)
```

### Custom FastAPI Agent Server

```python
# File: agents/product_transaction_agent/agent.py

def create_product_transaction_server() -> FastAPI:
    """Create FastAPI server for Product Transaction Agent"""

    agent = ProductTransactionAgent()

    # Define custom endpoint handlers
    async def register_product_endpoint(request: ProductRegistrationRequest = Body(...)):
        """POST /register-product-image"""
        return await agent.register_product_image(request)

    async def chat_transaction_endpoint(request: TransactionRequest = Body(...)):
        """POST /chat/transaction"""
        return await agent.process_chat_transaction(request)

    # Custom endpoints dictionary
    custom_endpoints = {
        "register-product-image": register_product_endpoint,
        "chat/transaction": chat_transaction_endpoint
    }

    # Simple task manager for /run endpoint
    class SimpleTaskManager:
        async def process_task(self, message: str, context: Dict, session_id: Optional[str]):
            return {
                "message": "Use specific endpoints: /register-product-image or /chat/transaction",
                "status": "info"
            }

    task_manager = SimpleTaskManager()

    # Create server using factory
    app = create_agent_server(
        name=agent.name,
        description=agent.description,
        task_manager=task_manager,
        endpoints=custom_endpoints
    )

    return app

# Create the app
app = create_product_transaction_server()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
```

---

## Tool Implementation Pattern

### Creating Tools for Google ADK Agents

```python
# File: agents/misc_transactions/tools/petty_cash_tool.py
from typing import Dict, Any
from common.misc_transactions_service import MiscTransactionsService

async def petty_cash_withdrawal_tool(
    user_id: str,
    amount: float,
    purpose: str,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Tool for recording petty cash withdrawals

    This function will be wrapped as a FunctionTool for Google ADK agents

    Args:
        user_id: Business owner identifier
        amount: Withdrawal amount (must be positive)
        purpose: Reason for withdrawal
        notes: Optional additional notes

    Returns:
        Dict with success, message, transaction_id, remaining_balance
    """
    try:
        # Validate input
        if amount <= 0:
            return {
                "success": False,
                "error": "Amount must be greater than 0"
            }

        # Call service layer
        service = MiscTransactionsService()
        result = await service.record_petty_cash_withdrawal(
            user_id,
            amount,
            purpose,
            notes
        )

        if result["success"]:
            # Format success response
            return {
                "success": True,
                "message": (
                    f"✅ Petty cash withdrawal recorded!\n\n"
                    f"💰 Amount: ${amount:.2f}\n"
                    f"📝 Purpose: {purpose}\n"
                    f"🏦 Remaining balance: ${result['remaining_balance']:.2f}\n"
                    f"📄 Transaction ID: {result['transaction_id']}"
                ),
                "transaction_id": result["transaction_id"],
                "remaining_balance": result["remaining_balance"]
            }
        else:
            return {
                "success": False,
                "error": f"❌ Failed: {result['error']}"
            }

    except Exception as e:
        logger.error(f"Error in petty_cash_withdrawal_tool: {str(e)}")
        return {
            "success": False,
            "error": f"❌ Error: {str(e)}"
        }

async def get_cash_balance_tool(user_id: str) -> Dict[str, Any]:
    """
    Tool for checking current cash balance
    """
    try:
        service = MiscTransactionsService()
        balance = await service.get_current_cash_balance(user_id)

        return {
            "success": True,
            "balance": balance,
            "message": f"💰 Current cash balance: ${balance:.2f}"
        }

    except Exception as e:
        logger.error(f"Error in get_cash_balance_tool: {str(e)}")
        return {
            "success": False,
            "error": f"❌ Error: {str(e)}"
        }
```

### Wrapping Tools for ADK Agents

```python
# File: agents/assistant/tools/financial_report_tool.py
from google.adk.tools import FunctionTool

def create_financial_report_tool(financial_service, user_service):
    """
    Create a FunctionTool for financial report generation
    """

    async def generate_financial_report_func(
        user_id: str,
        period: str = "today",
        include_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive financial report PDF

        Args:
            user_id: Store owner ID
            period: Time period (today, this week, this month, etc.)
            include_insights: Include AI-generated insights

        Returns:
            Dict with success, filename, firebase_url, summary
        """
        try:
            # Parse period and get date range
            start_date, end_date = parse_period(period)

            # Fetch financial data
            transactions = await financial_service.get_transactions(
                user_id,
                start_date,
                end_date
            )

            # Calculate metrics
            summary = calculate_financial_summary(transactions)

            # Generate PDF
            pdf_generator = PDFReportGenerator()
            pdf_content = pdf_generator.generate_financial_report(
                user_id,
                period,
                summary,
                transactions
            )

            # Upload to Firebase Storage
            filename = f"financial_report_{user_id}_{period}_{datetime.now().strftime('%Y%m%d')}.pdf"
            firebase_url = await upload_to_firebase(pdf_content, filename, user_id)

            return {
                "success": True,
                "filename": filename,
                "firebase_url": firebase_url,
                "download_url": firebase_url,
                "summary": summary,
                "period": period,
                "message": f"📊 Report generated for {period}"
            }

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Wrap as FunctionTool
    tool = FunctionTool(
        func=generate_financial_report_func,
        name="generate_financial_report",
        description=(
            "Generate comprehensive PDF financial reports for specified periods. "
            "Use ONLY when user explicitly requests a report. "
            "Periods: today, yesterday, this week, last week, this month, last month."
        )
    )

    return tool
```

---

## Deployment Guide

### Environment Setup

```bash
# .env file (create in project root)
# Google AI
GOOGLE_API_KEY=your_gemini_api_key_here

# Firebase
FIREBASE_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/firebase-service-account-key.json

# Server Configuration
STORE_AGENTS_HOST=127.0.0.1
STORE_AGENTS_PORT=8004

# AutoML (if using)
AUTOML_PROJECT_ID=your-gcp-project
AUTOML_MODEL_ID=your-model-id
```

### Dependencies

```txt
# requirements.txt

# Google AI & ADK
google-generativeai>=0.3.0
google-adk>=0.1.0
google-cloud-vision>=3.4.0
google-cloud-storage>=2.10.0
google-cloud-automl>=2.11.0

# LLM Integration
litellm>=1.0.0

# Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0

# Firebase
firebase-admin>=6.2.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
Pillow>=10.0.0

# PDF Generation
reportlab>=4.0.0

# Async Support
aiohttp>=3.9.0
```

### Installation

```bash
# 1. Clone/create project
mkdir my-agent-project
cd my-agent-project

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 5. Set up Firebase
# Download firebase-service-account-key.json from Firebase Console
# Place in project root or update GOOGLE_APPLICATION_CREDENTIALS path
```

### Running the Servers

```bash
# Terminal 1: Main Assistant Agent (Port 8004)
python -m agents.assistant

# Terminal 2: Product Transaction Agent (Port 8001)
python -m agents.product_transaction_agent.agent

# Terminal 3: Misc Transactions Agent (Port 8002)
python -m agents.misc_transactions.agent

# Terminal 4: Unified Chat Agent (Port 8003)
python unified_chat_agent.py
```

### Docker Deployment (Optional)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables (override in docker-compose)
ENV STORE_AGENTS_HOST=0.0.0.0
ENV STORE_AGENTS_PORT=8004

# Run server
CMD ["python", "-m", "agents.assistant"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  assistant-agent:
    build: .
    ports:
      - "8004:8004"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    volumes:
      - ./firebase-service-account-key.json:/app/firebase-service-account-key.json
    command: python -m agents.assistant

  product-agent:
    build: .
    ports:
      - "8001:8001"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    volumes:
      - ./firebase-service-account-key.json:/app/firebase-service-account-key.json
    command: python -m agents.product_transaction_agent.agent

  unified-chat:
    build: .
    ports:
      - "8003:8003"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    volumes:
      - ./firebase-service-account-key.json:/app/firebase-service-account-key.json
    command: python unified_chat_agent.py
```

### Testing

```bash
# Test health endpoint
curl http://localhost:8004/health

# Test agent endpoint
curl -X POST http://localhost:8004/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "context": {"user_id": "test_user_123"}
  }'

# Test unified chat
curl -X POST http://localhost:8003/run \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Check my inventory",
    "user_id": "test_user_123"
  }'

# Test product registration with image
curl -X POST http://localhost:8001/register-product-image \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_here",
    "user_id": "test_user_123",
    "is_url": false
  }'
```

---

## Best Practices

### 1. Agent Design Principles

**✅ DO:**
- Use ADK agents for coordination and natural language understanding
- Use FastAPI classes for deterministic business logic
- Keep tools focused on single responsibilities
- Provide clear, actionable error messages
- Log all agent decisions for debugging

**❌ DON'T:**
- Mix LLM calls with critical business logic
- Create circular dependencies between agents
- Skip input validation
- Return raw technical data to users
- Hardcode credentials

### 2. Error Handling

```python
# Good: Graceful degradation
try:
    result = await expensive_operation()
    if not result.get("success"):
        # Fallback to simpler method
        result = await simple_fallback_operation()
    return result
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {
        "success": False,
        "message": "We encountered an issue. Please try again.",
        "error": str(e)
    }

# Bad: Letting errors crash
result = await expensive_operation()  # Could fail
return result["data"]["nested"]["value"]  # Could fail
```

### 3. Performance Optimization

```python
# Fast path for common operations
if "image_data" in context:
    # Skip LLM, go straight to vision API
    return await vision_processor.process_image(...)

# Only use LLM when necessary
if requires_natural_language_understanding(message):
    return await agent.process(message)
else:
    return await deterministic_handler(message)
```

### 4. Testing Strategy

```python
# Unit test for tools
async def test_petty_cash_withdrawal_tool():
    result = await petty_cash_withdrawal_tool(
        user_id="test_user",
        amount=50.0,
        purpose="Office supplies"
    )
    assert result["success"] == True
    assert "transaction_id" in result

# Integration test for agent
async def test_product_registration_flow():
    agent = ProductTransactionAgent()
    request = ProductRegistrationRequest(
        image_data="base64_test_image",
        user_id="test_user",
        is_url=False
    )
    response = await agent.register_product_image(request)
    assert response.success == True
    assert response.product is not None
```

### 5. Security Considerations

```python
# Input validation
if not is_valid_user_id(user_id):
    raise HTTPException(status_code=400, detail="Invalid user ID")

# Path traversal prevention
if ".." in filename or "/" in filename:
    raise HTTPException(status_code=400, detail="Invalid filename")

# Rate limiting (use libraries like slowapi)
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/run")
@limiter.limit("10/minute")
async def run(request: AgentRequest):
    ...
```

### 6. Monitoring & Observability

```python
# Structured logging
logger.info(
    "Agent processing",
    extra={
        "user_id": user_id,
        "agent_type": agent_type,
        "message_length": len(message),
        "has_image": has_image
    }
)

# Performance tracking
start_time = time.time()
result = await process()
processing_time = time.time() - start_time
logger.info(f"Processed in {processing_time:.2f}s")

# Error tracking (use Sentry, etc.)
import sentry_sdk
sentry_sdk.capture_exception(exception)
```

---

## Project Structure Template

```
my-agent-project/
├── agents/
│   ├── assistant/
│   │   ├── __init__.py
│   │   ├── __main__.py              # Server entry point
│   │   ├── agent.py                 # Main coordinator agent
│   │   ├── task_manager.py          # ADK runner integration
│   │   ├── financial_reporting_subagent.py
│   │   ├── user_greeting_subagent.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       └── financial_report_tool.py
│   │
│   ├── product_transaction_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                 # FastAPI agent class
│   │   ├── models.py                # Pydantic models
│   │   └── helpers.py               # Business logic
│   │
│   └── misc_transactions/
│       ├── __init__.py
│       ├── agent.py
│       └── tools/
│           ├── petty_cash_tool.py
│           ├── owner_drawing_tool.py
│           └── cash_deposit_tool.py
│
├── common/
│   ├── __init__.py
│   ├── server.py                    # FastAPI server factory
│   ├── user_service.py              # User management
│   ├── product_service.py           # Product operations
│   ├── financial_service.py         # Financial operations
│   └── firebase_storage_service.py  # Cloud storage
│
├── unified_chat_agent.py            # Unified coordinator
├── requirements.txt
├── .env.example
├── .env
├── firebase-service-account-key.json
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Quick Start Checklist

### For Claude (or New Developers)

**To replicate this architecture in a new project:**

1. **Set Up Project Structure**
   - [ ] Create directory structure (see above)
   - [ ] Set up virtual environment
   - [ ] Install dependencies from requirements.txt

2. **Configure Services**
   - [ ] Set up Firebase project
   - [ ] Download service account key
   - [ ] Get Google AI API key
   - [ ] Create .env file with credentials

3. **Implement Core Components**
   - [ ] Copy `common/server.py` (FastAPI factory)
   - [ ] Implement TaskManager with ADK Runner
   - [ ] Create base Pydantic models

4. **Build Your First Agent**
   - [ ] Choose agent type (ADK or FastAPI)
   - [ ] Define request/response models
   - [ ] Implement agent logic
   - [ ] Create server entry point

5. **Add Tools (for ADK agents)**
   - [ ] Write business logic functions
   - [ ] Wrap as FunctionTool
   - [ ] Add to agent's tools list

6. **Test & Deploy**
   - [ ] Unit test tools
   - [ ] Integration test agents
   - [ ] Run locally
   - [ ] Deploy (Docker/Cloud)

---

## Conclusion

This architecture provides:

✅ **Scalability**: Add new agents without modifying existing ones
✅ **Flexibility**: Mix LLM intelligence with deterministic logic
✅ **Maintainability**: Clear separation of concerns
✅ **Performance**: Fast paths for common operations
✅ **Reliability**: Graceful error handling throughout

Use this documentation as a complete blueprint to build similar multi-agent systems with Google ADK and FastAPI.

---

**Document Version**: 1.0
**Last Updated**: 2025-01-15
**Project**: Store Agents Architecture
**Author**: AI Agent Development Team
