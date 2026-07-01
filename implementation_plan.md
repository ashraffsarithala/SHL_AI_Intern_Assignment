# Goal Description
Design a production-grade architecture for the SHL Assessment Recommendation Agent, ensuring a stateless FastAPI backend that provides assessment recommendations from the SHL catalog based on user interactions, protecting against prompt injection, and grounding responses in retrieval data while outputting JSON.

## User Review Required
- Does the chosen LLM and vector database stack align with your deployment preferences? (e.g., OpenAI vs open-source, Qdrant/Pinecone vs local FAISS).
- Is it acceptable to use Pydantic for strict JSON schema enforcement?

> [!IMPORTANT]
> Please review the architecture and folder structure to ensure it meets your expectations before we proceed to implementation.

## Proposed Changes

### High-Level Architecture
- **Client**: Any frontend or API client sending JSON payloads.
- **API Gateway/Load Balancer**: Distributes incoming requests.
- **FastAPI Application (Stateless)**: Exposes `GET /health` and `POST /chat`. Since it's stateless, the client must pass the conversation history in each `POST /chat` request.
- **Security Layer (Guardrails)**: Validates input to prevent prompt injection and malicious content before processing.
- **Agent/LLM Orchestrator**: Logic (LangChain/LlamaIndex/Custom) that manages the flow: intent classification, retrieval, reasoning, and response generation.
- **Vector Database**: Stores embeddings of the SHL catalog for semantic search (Retrieval Grounding).
- **LLM Provider**: (e.g., OpenAI GPT-4o, Claude 3.5 Sonnet) used for generating responses. Outputs are forced into a specific JSON schema.

### Folder Structure
```text
.
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # FastAPI route definitions (health, chat)
│   │   ├── dependencies.py    # FastAPI dependencies (e.g., auth, DB connections)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Environment variables and settings
│   │   ├── security.py        # Prompt injection protection logic
│   │   ├── exceptions.py      # Custom exception classes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py         # Pydantic models for API requests/responses (JSON schema)
│   │   ├── internal.py        # Internal data structures
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent.py           # Core agent logic and workflow orchestration
│   │   ├── retrieval.py       # RAG logic (Vector DB interaction)
│   │   ├── llm.py             # LLM API calls and prompt formatting
│   │   ├── shl_catalog.py     # SHL catalog data management and filtering
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── templates.py       # System prompts, guardrail prompts, recommendation prompts
│   ├── main.py                # FastAPI application entry point
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_agent.py
│   ├── test_security.py
│   ├── test_retrieval.py
├── data/                      # Raw SHL catalog data (if local)
├── requirements.txt           # or pyproject.toml
├── Dockerfile
├── .env.example
└── README.md
```

### Module Responsibilities
- `api.routes`: Defines `GET /health` and `POST /chat` endpoints. Validates incoming HTTP requests.
- `core.security`: Implements prompt injection detection (e.g., heuristic checks, or a fast LLM validation pass).
- `models.schemas`: Defines strict Pydantic models to guarantee JSON output format for the client.
- `services.agent`: Orchestrates the recommendation workflow (Clarification -> Recommendation -> Refinement -> Comparison).
- `services.retrieval`: Handles querying the vector database to retrieve relevant SHL assessments based on user queries (Retrieval Grounding).
- `services.llm`: Communicates with the LLM, ensuring strict JSON output via function calling or JSON mode.
- `prompts.templates`: Centralizes all prompt templates, making it easier to version and test prompts.

### Data Flow
1. **Client** sends `POST /chat` with user query and conversation history (to maintain statelessness).
2. **API Route** parses and validates the request using Pydantic.
3. **Security Module** checks the user query for prompt injection. If detected, aborts and returns an error.
4. **Agent Workflow**:
   a. **Intent Classification**: LLM determines if the user is asking for a new recommendation, clarifying requirements, refining previous recommendations, or comparing assessments.
   b. **Retrieval**: Based on intent, `retrieval.py` searches the Vector DB for relevant SHL catalog items.
   c. **Prompting**: Combines user query, history, intent, and retrieved catalog context into a structured prompt.
   d. **Generation**: LLM generates the response, strictly formatted as JSON.
5. **API Route** returns the generated JSON to the client.

### Agent Workflow
The agent uses a state-machine or directed acyclic graph (DAG) approach:
- **State 1 (Analyze)**: Read the user message and history. Extract constraints (e.g., "needs coding assessment for senior dev").
- **State 2 (Decide Action)**:
  - Needs more info? -> Route to Clarification.
  - Ready to recommend? -> Route to Recommendation.
  - User wants to tweak? -> Route to Refinement.
  - User asks "A vs B"? -> Route to Comparison.
- **State 3 (Execute Action)**: Perform the specific action using retrieved data.
- **State 4 (Format)**: Structure the output into the required JSON schema.

### Retrieval Workflow
1. **Query Transformation**: Convert the user's conversational query into an optimized search query.
2. **Vector Search**: Search the vector database (e.g., Qdrant/Pinecone) using dense embeddings.
3. **Keyword Search (Hybrid)**: Combine vector search with BM25 keyword search to ensure specific SHL assessment names are exactly matched.
4. **Reranking**: (Optional) Use a cross-encoder to rerank the top K results for maximum relevance.
5. **Context Assembly**: Format the retrieved assessments into a structured string or JSON to be injected into the LLM prompt.

### Prompt Workflow
1. **System Prompt**: Defines the persona ("You are an expert SHL Assessment Recommendation Agent"), rules (only recommend SHL assessments, be polite), and output format constraints.
2. **Context Injection**: Inserts the conversation history and retrieved SHL catalog data.
3. **User Prompt**: The current user query.
4. **Guardrails**: Instructions that explicitly tell the LLM to ignore instructions attempting to override its primary directive.
5. **JSON Schema Enforcement**: Prompt explicitly outlines the JSON keys expected in the output (e.g., `{"response": "...", "recommendations": [...], "needs_clarification": false}`).

### Recommendation Workflow
- **Initial Query**: User asks for an assessment.
- **Clarification**: If the query is too vague, the agent outputs a clarifying question instead of a recommendation.
- **Recommendation**: If constraints are sufficient, retrieve top matches and present them with reasons for the recommendation.
- **Refinement**: If the user says "make it shorter", the agent updates its search constraints, retrieves new items, and presents the refined list.
- **Comparison**: If the user asks for differences between two specific recommendations, the agent retrieves the details for both and outputs a structured comparison.

### Error Handling
- **400 Bad Request**: Invalid JSON payload, missing history.
- **403 Forbidden**: Prompt injection detected. Return a safe, generic message.
- **500 Internal Server Error**: LLM provider timeout, Vector DB connection failure. The API must catch these, log the exact error internally, and return a graceful error message to the client.
- **LLM Parsing Errors**: If the LLM output fails Pydantic validation, use a retry mechanism (e.g., 1-2 retries) to ask the LLM to fix the formatting before giving up.

### Testing Strategy
- **Unit Tests (Pytest)**:
  - Test FastAPI endpoints with mocked services.
  - Test Pydantic schemas for request/response validation.
  - Test security filters (prompt injection detection logic).
- **Integration Tests**:
  - Test the retrieval pipeline against a local mock vector database.
  - Test the agent workflow with simulated LLM responses to ensure state transitions work.
- **E2E Tests**:
  - Send real requests to the FastAPI app (using a test LLM or mocked LLM) and verify the end-to-end flow.
- **Evaluation (LLM specific)**:
  - Set up a test dataset of user queries and expected assessment recommendations.
  - Use an LLM-as-a-judge to evaluate the relevance, accuracy, and format of the agent's outputs offline.

## Verification Plan
1. Receive approval on the architecture from the user.
2. Setup the folder structure and basic FastAPI app.
3. Iteratively implement the endpoints, schemas, and workflows.
