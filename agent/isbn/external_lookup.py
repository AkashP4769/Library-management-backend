"""
External library database lookup for book information.

This module provides:
- Search against OpenLibrary API
- ISBN extraction and book metadata retrieval
- Cover image URL resolution
"""

import logging
from typing import Optional

import requests

from agent.schemas import BookMetadata

logger = logging.getLogger(__name__)

OPEN_LIBRARY_BASE_URL: str = "https://openlibrary.org/search.json"
MAX_RESULTS: int = 10


def search_book(book_metadata: BookMetadata) -> list[dict]:
    """
    Search for books in OpenLibrary matching the given metadata.

    Args:
        book_metadata: Book information with title, author, and language

    Returns:
        List of matching books with title, author, ISBN, and cover URLs.
        Each book is a dict with keys: title, author, isbn, links
    """
    if not book_metadata:
        raise ValueError("Book metadata cannot be empty")

    if not book_metadata.title or not book_metadata.author:
        logger.warning(
            "Incomplete metadata - Title: %s, Author: %s",
            book_metadata.title,
            book_metadata.author,
        )
        return []

    try:
        logger.info(
            "Searching OpenLibrary for: Title=%s, Author=%s, Language=%s",
            book_metadata.title,
            book_metadata.author,
            book_metadata.language,
        )

        # Build search URL
        url = (
            f"{OPEN_LIBRARY_BASE_URL}"
            f"?title={book_metadata.title}"
            f"&author={book_metadata.author}"
            f"&language={book_metadata.language.value}"
            f"&limit={MAX_RESULTS}"
        )

        logger.debug("OpenLibrary API URL: %s", url)

        # Make request to OpenLibrary
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        docs = data.get("docs", [])

        logger.info("OpenLibrary returned %d results", len(docs))

        books = []

        # Process each result
        for doc in docs:
            try:
                book_dict = _format_book_result(doc)
                if book_dict:
                    books.append(book_dict)
                    logger.debug(
                        "Added book: %s by %s",
                        book_dict.get("title"),
                        book_dict.get("author"),
                    )
            except (ValueError, KeyError) as e:
                logger.warning("Failed to format book result: %s", e)
                continue

        logger.info("Formatted %d books from OpenLibrary results", len(books))

        return books

    except requests.RequestException as e:
        logger.error("OpenLibrary API request failed: %s", e)
        raise
    except Exception as e:
        logger.error("Book search failed: %s", e)
        raise


def _extract_isbn(doc: dict) -> str:
    """
    Extract ISBN from OpenLibrary document.

    Args:
        doc: OpenLibrary document dict

    Returns:
        ISBN string or "N/A" if not found
    """
    # Try to get ISBN from various fields
    if "isbn" in doc and doc["isbn"]:
        return doc["isbn"][0]

    # Try identifier array with isbn_ prefix
    if "ia" in doc and doc["ia"]:
        for identifier in doc["ia"]:
            if identifier.startswith("isbn_"):
                isbn = identifier.replace("isbn_", "").replace("_", "")
                if isbn:
                    return isbn

    return "N/A"


def _get_cover_url(doc: dict) -> Optional[str]:
    """
    Get cover image URL from OpenLibrary document.

    Tries multiple sources in order of preference.

    Args:
        doc: OpenLibrary document dict

    Returns:
        Cover image URL or None if not available
    """
    # Try cover_edition_key first (most reliable)
    if doc.get("cover_edition_key"):
        return f"https://covers.openlibrary.org/b/olid/{doc['cover_edition_key']}-L.jpg"

    # Try cover_i (cover ID)
    if doc.get("cover_i"):
        return f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"

    # Try to get from ISBN if available
    isbn = _extract_isbn(doc)
    if isbn and isbn != "N/A":
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

    return None


def _format_book_result(doc: dict) -> Optional[dict]:
    """
    Format an OpenLibrary document into standardized book dict.

    Args:
        doc: OpenLibrary document from API response

    Returns:
        Formatted book dict with title, author, isbn, links
        or None if essential fields are missing
    """
    title = doc.get("title")
    author_list = doc.get("author_name", [])
    author = author_list[0] if author_list else "Unknown"

    if not title:
        logger.debug("Skipping book without title")
        return None

    isbn = _extract_isbn(doc)
    cover_url = _get_cover_url(doc)

    return {
        "title": title,
        "author": author,
        "isbn": isbn,
        "links": cover_url,
    }
