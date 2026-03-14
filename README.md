# Project Wright

An AI-powered autonomous writing assistant that takes a draft and produces a publication-ready manuscript through a multi-agent pipeline.

## Tech Stack

- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Agents:** LangGraph, LangChain, Ollama (Llama 3.1 8B)
- **Task Queue:** Celery + Redis
- **Story Base:** MongoDB
- **Frontend:** React, Zustand, TailwindCSS

## Prerequisites

- Python 3.12.3
- Docker + Docker Compose
- Git

## Local Setup

1. Clone the repo
   git clone <repo-url>
   cd project-wright

2. Copy environment file
   cp .env.example .env

   # Edit .env and fill in your secrets

3. Start databases
   docker compose up -d
   docker compose ps # wait until all show "healthy"

4. Create Python virtual environment
   python3.12 -m venv .venv
   source .venv/bin/activate

5. Install dependencies
   pip install -r backend/requirements.txt

6. Install pre-commit hooks
   pre-commit install

7. Verify pre-commit works
   pre-commit run --all-files

## Local Development Setup

### Ollama Installation & Configuration

Ollama provides the LLM inference API required by the agent pipeline. **Ollama must be running before starting FastAPI.**

1. Install Ollama:
   ```bash
   # macOS
   brew install ollama

   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh

   # Windows
   # Download from https://ollama.ai/download
   ```

2. Start the Ollama service:
   ```bash
   ollama serve
   ```
   This starts the API server on `http://localhost:11434`

3. Pull the required models in another terminal:
   ```bash
   # Current model (Week 1-6)
   ollama pull qwen3.5:4b

4. Verify Ollama is reachable:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   You should see a JSON response listing your pulled models.

**Important:** Ollama must be running before you start the FastAPI backend. If FastAPI starts without Ollama, it will fail when trying to initialize the agent pipeline.

## CI

GitHub Actions runs on every push/PR to main and develop.
Three checks must pass: lint, backend-tests, docker-validate.

## Project Structure

- `/backend` — FastAPI application
- `/frontend` — React SPA
- `/agents` — LangGraph agent definitions
- `/infra` — Docker, Nginx, deployment configs
