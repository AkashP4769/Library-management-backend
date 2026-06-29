"""
ISBN extraction pipeline from book cover images.

This module orchestrates the process of:
1. Extracting text from cover images using OCR
2. Parsing book metadata from OCR text with LLM
3. Looking up books in external library databases
"""

import logging

from agent.isbn.vision_chain import extract_text, parse_book
from agent.isbn.external_lookup import search_book

logger = logging.getLogger(__name__)


def isbn_pipeline(image_path: str) -> list[dict]:
    """
    Extract book information from a cover image.

    This pipeline:
    1. Reads image file and extracts text using OCR
    2. Uses LLM to parse book metadata (title, author, language)
    3. Searches external library databases for matching books

    Args:
        image_path: Path to the book cover image file

    Returns:
        List of matching books with ISBN, title, author, cover URLs
    """
    try:
        logger.info("Starting ISBN extraction pipeline for: %s", image_path)

        # Step 1: Extract text from image using OCR
        logger.debug("Extracting text from image")
        text = extract_text(image_path)

        if not text or not text.strip():
            logger.warning("No text extracted from image: %s", image_path)
            return []

        logger.debug("Extracted text (first 100 chars): %s", text[:100])

        # Step 2: Parse book metadata using LLM
        logger.debug("Parsing book metadata from OCR text")
        book_metadata = parse_book(text)

        if not book_metadata:
            logger.warning("Failed to parse book metadata")
            return []

        logger.info(
            "Parsed metadata - Title: %s, Author: %s, Language: %s",
            book_metadata.title,
            book_metadata.author,
            book_metadata.language,
        )

        # Step 3: Search for books in external databases
        logger.debug("Searching for books in external library")
        books = search_book(book_metadata)

        logger.info("Found %d matching books", len(books))

        return books

    except FileNotFoundError as e:
        logger.error("Image file not found: %s", image_path)
        raise ValueError(f"Image file not found: {image_path}") from e
    except Exception as e:
        logger.error("ISBN pipeline failed: %s", e)
        raise
