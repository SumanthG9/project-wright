# Project Wright

An AI-powered autonomous writing assistant that takes a draft and produces a publication-ready manuscript through a multi-agent pipeline.

## Tech Stack
- **Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic
- **Agents:** LangGraph, LangChain, Ollama (Llama 3.1 8B)
- **Task Queue:** Celery + Redis
- **Story Base:** MongoDB
- **Frontend:** React, Zustand, TailwindCSS

## Local Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- Ollama (https://ollama.ai)

### Getting Started

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in values
3. Run `docker-compose up -d` to start all services
4. See each sub-folder's README for further setup

## Project Structure
- `/backend` — FastAPI application
- `/frontend` — React SPA
- `/agents` — LangGraph agent definitions
- `/infra` — Docker, Nginx, deployment configs
