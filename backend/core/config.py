import os
from pathlib import Path

from dotenv import load_dotenv

print(Path(__file__).resolve().parents[2] / ".env")
load_dotenv(
    Path(__file__).resolve().parents[2] / ".env"
)  # reads .env from the project root

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
REDIS_URL = os.getenv("REDIS_URL")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
