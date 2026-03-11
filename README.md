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

## CI

GitHub Actions runs on every push/PR to main and develop.
Three checks must pass: lint, backend-tests, docker-validate.

## Project Structure

- `/backend` — FastAPI application
- `/frontend` — React SPA
- `/agents` — LangGraph agent definitions
- `/infra` — Docker, Nginx, deployment configs
