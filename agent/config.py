"""
Configuration settings for the agent module.

This module centralizes all agent-related configuration including:
- LLM settings
- Storage paths
- Vector store settings
- RAG parameters
"""

from pathlib import Path
from typing import Final

# Directory Configuration
AGENT_DIR: Final = Path(__file__).parent
STORAGE_DIR: Final = AGENT_DIR / "storage"
UPLOADS_DIR: Final = STORAGE_DIR / "uploads"
CHROMA_DB_DIR: Final = AGENT_DIR / "chroma_db"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

# LLM Configuration
LLM_MODEL: Final = "groq/qwen/qwen3-32b"
LLM_TEMPERATURE: Final = 0.3

# RAG Configuration
CHUNK_SIZE: Final = 300
CHUNK_OVERLAP: Final = 50
COLLECTION_NAME: Final = "documents"

# File Upload Configuration
ALLOWED_EXTENSIONS: Final = {".pdf", ".txt", ".md", ".docx", ".jpeg", ".jpg", ".png"}
