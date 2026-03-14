import os
from pathlib import Path

from dotenv import load_dotenv

print(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)  # reads .env from the project root

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
ALEMBIC_DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
REDIS_URL = os.getenv("REDIS_URL")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Pipeline mode — "local" or "cloud"
PIPELINE_MODE = os.getenv("PIPELINE_MODE", "local")

# Local model profile
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "qwen3.5:4b")

# Cloud model profile (values unused until Week 7 resolver is built)
CLOUD_MODEL_IDC = os.getenv("CLOUD_MODEL_IDC", "qwen3-next:80b-cloud")
CLOUD_MODEL_SB = os.getenv("CLOUD_MODEL_SB", "qwen3-coder-next-cloud")
CLOUD_MODEL_RP = os.getenv("CLOUD_MODEL_RP", "deepseek-v3.2-cloud")
CLOUD_MODEL_OS = os.getenv("CLOUD_MODEL_OS", "qwen3-next:80b-cloud")
CLOUD_MODEL_DF = os.getenv("CLOUD_MODEL_DF", "qwen3.5:122b-cloud")
CLOUD_MODEL_CH = os.getenv("CLOUD_MODEL_CH", "kimi-k2-thinking-cloud")
CLOUD_MODEL_BR = os.getenv("CLOUD_MODEL_BR", "nemotron-3-nano:30b-cloud")
