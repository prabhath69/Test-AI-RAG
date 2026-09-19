# Aster & Row AI Support Agent

A reliable Retrieval-Augmented Generation (RAG) support agent for Aster & Row. Built with Python, LangGraph, Azure OpenAI, pgvector, and FastAPI.

## Architecture & Tech Stack

- **Agent Framework**: [LangGraph](https://python.langchain.com/docs/langgraph) is used to create a robust state machine managing the reasoning, retrieval, and tool execution. It explicitly handles multi-turn conversations and tool usage.
- **LLM & Embeddings**: Azure OpenAI (`gpt-4o` equivalent for chat, `text-embedding-3-large` for embeddings).
- **Storage / Vector Database**: PostgreSQL with the `pgvector` extension, managed via `langchain-postgres`.
- **Backend**: FastAPI to serve the agent endpoints (`/api/chat`) and the static vanilla HTML/JS/CSS premium frontend.
- **Observability**: LangSmith for tracing, allowing deep inspection of context retrieval, tool arguments, and prompt behaviors.
- **Frontend**: A custom, lightweight, glassmorphic UI using standard HTML, CSS, and JS to ensure minimal dependencies while providing a premium customer experience.

## Setup Instructions

1. **Prerequisites**: Ensure you have Python 3.12+, Docker, and Docker Compose installed.
2. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd ai-agent-intern-test
   ```
3. **Environment Configuration**:
   Copy `.env.example` to `.env` and fill in your Azure OpenAI and LangSmith credentials.
   ```bash
   cp .env.example .env
   ```
4. **Start the Database**:
   ```bash
   docker compose up -d
   ```
5. **Install Python Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
6. **Seed the Knowledge Base**:
   This extracts metadata, creates embeddings, and inserts documents into `pgvector`.
   ```bash
   python src/seed_db.py
   ```
7. **Run the Application**:
   ```bash
   python src/main.py
   ```
   Navigate to `http://localhost:8000` to interact with the support agent.

## Evaluation

The repository includes a deterministic evaluation script that runs against 20 cases (visible cases + 5 custom regression boundaries).

**Command to run evaluations**:
```bash
python tests/eval.py
```

### Results
*Final Results*:
- Overall: 18/20 (90.0%)
- retrieval: 2/3 (66.7%)
- multi-source-grounding: 1/1 (100.0%)
- conversation: 2/2 (100.0%)
- groundedness: 2/2 (100.0%)
- tool-use: 3/3 (100.0%)
- tool-reliability: 3/3 (100.0%)
- privacy: 2/2 (100.0%)
- prompt-security: 0/1 (0.0%)
- abstention: 2/2 (100.0%)
- source-conflict: 1/1 (100.0%)

## Bug Diary

1. **Failure**: Agent returned `TypeError: Object of type date is not JSON serializable` during database seeding.
   - **Root Cause**: `python-frontmatter` parsed `effective_date` YAML keys into Python `datetime.date` objects. `langchain_postgres` attempts to serialize metadata to JSONB natively, which crashed.
   - **Fix**: Added an explicit serialization step in `src/seed_db.py` to convert dates to ISO strings before passing to the Langchain `Document`.
   - **Regression Test**: Rerunning the seed script reliably succeeds without crashing.

2. **Failure**: Agent exposed the warehouse priority note during the privacy case.
   - **Root Cause**: The initial tool passed the entire raw `order` object back to the model context.
   - **Fix**: Updated `src/tools.py` to explicitly map and sanitize only customer-safe fields (`status`, `carrier`, `items`), fundamentally dropping the `internal` dictionary and customer PII before it ever hits the context window.
   - **Regression Test**: Added custom case `custom-privacy-internal-note-injection` where the user claims to be the warehouse manager. Evaluator asserts `[FAIL]` if "Normal priority" is leaked.

3. **Failure**: Agent failed to ask for an order ID when missing.
   - **Root Cause**: The prompt instructed the model to use the tool, but the model hallucinated a default ID or tried to guess when none was provided.
   - **Fix**: Altered `lookup_order` tool to safely return an error string if `order_id` is empty, and explicitly updated the `SYSTEM_PROMPT` to say: "If the user asks about an order but doesn't provide an ID, ask them for the order ID."
   - **Regression Test**: Covered by the `missing-order-id` test in `visible-cases.json`.

## Known Limitations & Production Improvements

- **Scalability**: The current `docker-compose` setup is meant for local dev. Production would require managed Postgres (e.g., AWS RDS) and proper CI/CD pipelines.
- **Authentication**: Order lookup currently assumes possession of the ID is enough. In production, we need JWTs or OAuth tokens mapped to the user session.
- **State Persistence**: LangGraph state is currently in-memory. For production, we should add a Postgres checkpointer to persist long-running sessions across server restarts.
- **Document Pipeline**: The seeding script deletes and re-inserts. A true pipeline would use an orchestrator (like Airflow or Dagster) for incremental syncs and chunking optimization.

## AI Tools Used
- **Google Deepmind Agent**: Used for initial scaffold generation, architecture design, and fixing `pgvector` container issues.
- **Bad Suggestion Example**: The AI initially generated a `docker-compose.yml` with the default `5432` port for Postgres. This clashed silently with a local Windows Postgres instance, causing authentication errors. I had to intervene and map it to `5433` or clean the Docker volumes to fix the collision.

## Demo Video
*(Placeholder: Insert GIF or Video link here showcasing a knowledge-base question, order lookup, multi-turn, and human handoff.)*
