- `[ ]` **Phase 1: Project Setup**
  - `[ ]` Create folder structure (`src/api`, `src/agent`, `src/catalog`, `src/llm`, `src/models`, `src/core`, `src/utils`, `src/evaluation`, `tests/unit`, `tests/integration`, `tests/api`, `tests/evaluation`, `data/raw`, `data/processed`, `data/vector_index`)

- `[ ]` **Phase 1.5: Project Configuration**
  - `[ ]` Implement `core/config.py` (Environment, LLM, Vector DB settings)
  - `[ ]` Implement `core/logging.py` (Logging configuration)
  - `[ ]` Implement `core/exceptions.py` (Custom exceptions)
  - `[ ]` Implement `core/types.py` (Shared type definitions, aliases, common interfaces)

- `[ ]` **Phase 2: Core Models**
  - `[ ]` Implement internal models (`models/message.py`, `models/conversation.py`, `models/assessment.py`, `models/recommendation.py`, `models/metadata.py`)
  - `[ ]` Implement `models/conversation_state.py` (Structured state, constraints, intent, stage, missing info, normalized context)
  - `[ ]` Implement API models (`api/schemas.py`)

- `[ ]` **Phase 3A: Catalog Processing**
  - `[ ]` Implement `catalog/parser.py`
  - `[ ]` Implement `catalog/normalizer.py`
  - `[ ]` Implement `catalog/metadata_builder.py`

- `[ ]` **Phase 3B: Search Index**
  - `[ ]` Implement `catalog/embedding_builder.py`
  - `[ ]` Implement `catalog/index_builder.py`
  - `[ ]` Implement `catalog/cache.py`
  - `[ ]` Implement `catalog/catalog_loader.py`
  - `[ ]` Implement `catalog/catalog_repository.py` (Centralized access by name/ID/URL/metadata)

- `[ ]` **Phase 4: Conversation Understanding**
  - `[ ]` Implement `agent/scope_guard.py`
    - *Validates: Prompt Injection, Out-of-Scope Requests, Catalog Scope, Response Safety*
  - `[ ]` Implement `agent/conversation_manager.py`
  - `[ ]` Implement `agent/analyzer.py`
  - `[ ]` Implement `agent/decision_engine.py`
  - `[ ]` Implement `core/state_machine.py` and `core/constants.py` (Enums)

- `[ ]` **Phase 5: Retrieval & Recommendation**
  - `[ ]` Implement `agent/retriever.py`
  - `[ ]` Implement `agent/metadata_filter.py`
  - `[ ]` Implement `agent/recommendation_engine.py`
  - `[ ]` Implement `agent/comparison_engine.py`

- `[ ]` **Phase 6: LLM & Response Generation**
  - `[ ]` Implement `llm/prompt_builder.py`
  - `[ ]` Implement `llm/client.py`
  - `[ ]` Implement `llm/prompt_templates.py`
  - `[ ]` Implement `llm/output_parser.py`
  - `[ ]` Implement `agent/response_generator.py`
  - `[ ]` Implement `agent/json_formatter.py`

- `[ ]` **Phase 7: Utilities**
  - `[ ]` Implement `utils/helpers.py`
  - `[ ]` Implement `utils/validators.py`
  - `[ ]` Implement `utils/text_utils.py`
  - `[ ]` Implement `utils/ranking_utils.py`

- `[ ]` **Phase 8: API (FastAPI)**
  - `[ ]` Implement endpoints (`api/routes.py`)
  - `[ ]` Implement dependency injection (`api/dependencies.py`)
  - `[ ]` Wire application (`main.py`)

- `[ ]` **Phase 9: Evaluation Framework**
  - `[ ]` Implement `evaluation/golden_dataset.py`
  - `[ ]` Implement `evaluation/conversation_replayer.py`
  - `[ ]` Implement `evaluation/metrics.py`
  - `[ ]` Implement `evaluation/evaluator.py`
  - `[ ]` Implement `evaluation/failure_analysis.py`
  - `[ ]` Implement `evaluation/report_generator.py`

- `[ ]` **Phase 10: Testing**
  - `[ ]` Write `tests/unit/` tests
  - `[ ]` Write `tests/integration/` tests
  - `[ ]` Write `tests/api/` tests
  - `[ ]` Write `tests/evaluation/` tests
  - `[ ]` Implement JSON Contract Tests
    - *Verify exact request/response schema, required fields, field types, recommendation count, end_of_conversation behavior*

- `[ ]` **Phase 11: Documentation & Submission**
  - `[ ]` Write Architecture overview
  - `[ ]` Document Project Workflow (Runtime pipeline diagram)
  - `[ ]` Document API Specification (GET /health, POST /chat, Schemas, JSON Examples, Errors)
  - `[ ]` Write Setup instructions
  - `[ ]` Document Design decisions & Limitations
  - `[ ]` Write Instructions for running evaluation
  - `[ ]` Configure Docker & README
