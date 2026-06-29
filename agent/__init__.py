"""Agent module for library operations.

Main components:
- LibraryAgent: Core AI agent for processing library queries
- RAGService: Document indexing and semantic search
- Tools: Available agent tools for book search and policy queries
"""

from agent.schemas import AgentMessage, AgentResponse
from agent.library_agent import LibraryAgent, get_agent
from agent.rag_service import get_rag_service, RAGService

__all__ = [
    "AgentMessage",
    "AgentResponse",
    "LibraryAgent",
    "get_agent",
    "RAGService",
    "get_rag_service",
]
