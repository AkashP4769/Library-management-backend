"""
Tool definitions for the Library Agent.

This module defines all tools available to the agent for:
- Searching books
- Querying policy documents
- Retrieving library information
"""

import logging
from typing import Optional

from sqlalchemy import select, and_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import tool

from models.book import Book
from models.book_copy import BookCopy
from agent.rag_service import get_rag_service
import book.repo as books_repo
from borrowed_book import repo as borrowed_repo

logger = logging.getLogger(__name__)


def create_search_books_tool(db_session: AsyncSession):
    """
    Factory function to create a search_books tool with database session.

    Args:
        db_session: SQLAlchemy async database session

    Returns:
        Langchain tool function for searching books
    """

    @tool
    async def search_books(
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        isbn: Optional[str] = None,
        language: Optional[str] = None,
        available_only: bool = False,
        limit: int = 10,
    ) -> list[dict]:
        """
        Search books using flexible optional filters.

        This function provides a unified retrieval interface for the library system,
        allowing searches across multiple book attributes for chatbot and
        recommendation workflows.

        Args:
            title: Partial match on book title
            author: Partial match on author name
            genre: Partial match on genre/category
            isbn: Exact ISBN lookup
            language: Partial match on language
            available_only: Return only available books
            limit: Maximum number of results (max: 100)

        Returns:
            List of books matching all provided filters

        Examples:
            Search fantasy books:
                search_books(genre="Fantasy")

            Available Malayalam thrillers:
                search_books(
                    genre="Thriller",
                    language="Malayalam",
                    available_only=True
                )
        """
        # Validate inputs
        limit = min(limit, 100)  # Cap at 100
        if limit < 1:
            raise ValueError("Limit must be at least 1")

        filters = [Book.deleted_at.is_(None)]

        # Add filters based on provided parameters
        if title:
            filters.append(Book.title.ilike(f"%{title}%"))

        if author:
            filters.append(Book.author.ilike(f"%{author}%"))

        if genre:
            filters.append(Book.genre.ilike(f"%{genre}%"))

        if isbn:
            filters.append(Book.isbn == isbn)

        if language:
            filters.append(Book.language.ilike(f"%{language}%"))

        # Handle availability filter
        copy_stmt = select(BookCopy).where(BookCopy.isbn == Book.isbn)
        copy_result = await db_session.execute(copy_stmt)
        copies = copy_result.scalars().all()

        try:
            # Execute query
            stmt = select(Book).where(and_(*filters)).limit(limit)
            result = await db_session.execute(stmt)
            books = result.scalars().all()

            logger.info(
                "Found %d books with filters: title=%s, author=%s, genre=%s, isbn=%s, available=%s",
                len(books),
                title,
                author,
                genre,
                isbn,
                available_only,
            )

            # Convert to dictionaries for tool output
            return [
                {
                    "title": book.title,
                    "author": book.author,
                    "isbn": book.isbn,
                    "genre": book.genre,
                    "language": book.language,
                    "available": any(copy.status == "AVAILABLE" for copy in copies),
                }
                for book in books
            ]

        except Exception as e:
            logger.error("Book search failed: %s", e)
            raise

    return search_books


def create_query_documents_tool():
    """
    Factory function to create a query_documents tool.

    Returns:
        Langchain tool function for searching policy documents
    """

    @tool
    def query_documents(query: str) -> str:
        """
        Search HR/company policy documents using semantic search.

        This tool searches the library's policy documents to provide
        information about library rules, procedures, and guidelines.

        Args:
            query: Natural language question about policies

        Returns:
            Relevant policy information from the knowledge base

        Examples:
            query_documents("What are the borrowing limits?")
            query_documents("How do I reserve a book?")
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            rag_service = get_rag_service()
            context = rag_service.search_documents(query)
            logger.info("Retrieved policy context for: %s", query[:50])
            return context

        except Exception as e:
            logger.error("Document query failed: %s", e)
            raise

    return query_documents


def create_shelf_location_tool(db_session: AsyncSession):

    @tool
    async def shelf_location(isbn: str) -> list[dict]:
        """
        Retrieve shelf locations for available copies of a book using ISBN.

        Args:
            isbn: Book ISBN

        Returns:
            List of shelf details where the book is available.
        """

        if not isbn:
            raise ValueError("ISBN is required")

        try:
            shelves = await books_repo.get_shelves_of_book(
                db_session,
                isbn,
            )

            return {
                "found": len(shelves) > 0,
                "shelves": [
                    {
                        "shelf_id": shelf.id,
                        "shelf_code": shelf.shelf_code,
                        "shelf_location": shelf.office_location,
                        "capacity": shelf.capacity,
                    }
                    for shelf in shelves
                ],
            }

        except Exception as e:
            logger.error("Shelf lookup failed: %s", e)
            raise

    return shelf_location


def borrowed_books_tool(db_session: AsyncSession):

    @tool
    async def borrowed_books(user_id: int) -> list[dict]:
        """
        Retrieve borrowing history of a user.

        Args:
            user_id: User ID

        Returns:
            List of borrowed books with status.
        """

        if not user_id:
            raise ValueError("User ID is required")

        try:
            records = await borrowed_repo.get_user_borrow_history(
                db_session,
                user_id,
            )

            return {
                "has_history": len(records) > 0,
                "borrowed_books": [
                    {
                        "title": book.title,
                        "author": book.author,
                        "isbn": book.isbn,
                        "borrowed_at": borrowed.created_at,
                        "due_date": borrowed.due_date,
                        "returned_at": borrowed.returned_at,
                        "status": borrowed.status,
                    }
                    for borrowed, book in records
                ],
            }

        except Exception as e:
            logger.error("Borrow history lookup failed: %s", e)
            raise

    return borrowed_books


def create_agent_tools(db_session: AsyncSession) -> list:
    """
    Create all tools available to the agent.

    Args:
        db_session: SQLAlchemy async database session

    Returns:
        List of tool functions for the agent
    """
    return [
        create_search_books_tool(db_session),
        create_query_documents_tool(),
        create_shelf_location_tool(db_session),
        borrowed_books_tool(db_session),
    ]
