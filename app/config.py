# app/config.py
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "Jz7c[[AMBi9j5yS)"),
    "host": os.getenv("DB_HOST", "34.57.51.199"),
    "port": os.getenv("DB_PORT", "5432")
}

# Connection string format
DB_CONNECTION_STRING = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

# Application settings
MAX_CANDIDATES = int(os.getenv("MAX_CANDIDATES", "4"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))

# Logging settings
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))

# Paths
RESULTS_DIR = os.getenv("RESULTS_DIR", "data/results")

