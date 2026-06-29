"""
Vision and LLM-based text extraction and book metadata parsing.

This module provides:
- OCR text extraction from images
- LLM-powered book metadata parsing
- Structured output for book information
"""

import logging
from pathlib import Path
from typing import Optional, Any

import easyocr
from langchain_openai import ChatOpenAI

from agent.schemas import BookMetadata
from config import setting

logger = logging.getLogger(__name__)

# Initialize LLM for structured output
_llm: Optional[ChatOpenAI] = None
_structured_llm: Optional[Any] = None
_ocr_reader: Optional[easyocr.Reader] = None


def get_llm():
    """
    Get or create LLM instance (lazy initialization).

    Returns:
        ChatOpenAI instance configured with structured output
    """
    global _llm, _structured_llm

    if _llm is None:
        logger.info("Initializing LLM for book metadata parsing")
        _llm = ChatOpenAI(
            api_key=setting.litellm_api_key,
            base_url=setting.litellm_base_url,
            model="openai/gpt-oss-20b",
        )
        _structured_llm = _llm.with_structured_output(BookMetadata)

    return _structured_llm


def get_ocr_reader():
    """
    Get or create OCR reader instance (lazy initialization).

    Supports multiple languages for international book covers.

    Returns:
        easyocr.Reader instance
    """
    global _ocr_reader

    if _ocr_reader is None:
        logger.info("Initializing OCR reader with language support: en, fr, de, es, it")
        _ocr_reader = easyocr.Reader(["en", "fr", "de", "es", "it"])

    return _ocr_reader


def extract_text(image_path: str) -> str:
    """
    Extract text from an image using OCR.

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text from the image

    Raises:
        FileNotFoundError: If image doesn't exist
        Exception: If OCR processing fails
    """
    try:
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info("Extracting text from image: %s", image_path)

        reader = get_ocr_reader()
        ocr_results = reader.readtext(str(image_path))

        if not ocr_results:
            logger.warning("No text detected in image: %s", image_path)
            return ""

        # Extract text from OCR results (tuples of (bbox, text, confidence))
        extracted_text = "\n".join([result[1] for result in ocr_results])
        confidence_scores = [result[2] for result in ocr_results]

        avg_confidence = sum(confidence_scores) / len(confidence_scores)

        logger.info(
            "Extracted %d lines with avg confidence: %.2f",
            len(ocr_results),
            avg_confidence,
        )
        logger.debug("Extracted text (first 200 chars): %s", extracted_text[:200])

        return extracted_text

    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error("OCR extraction failed: %s", e)
        raise


def parse_book(ocr_text: str) -> Optional[BookMetadata]:
    """
    Parse book metadata from OCR text using structured LLM output.

    Uses an LLM to:
    - Extract book title (ignoring decorative text)
    - Extract author name
    - Infer language from text

    Args:
        ocr_text: Raw text extracted from image via OCR

    Returns:
        BookMetadata with title, author, and language, or None if parsing fails

    Raises:
        ValueError: If OCR text is empty
        Exception: If LLM parsing fails
    """
    if not ocr_text or not ocr_text.strip():
        raise ValueError("OCR text cannot be empty")

    try:
        logger.info("Parsing book metadata from OCR text")

        structured_llm = get_llm()

        prompt = f"""Extract the book title and author from this OCR text.
Ignore publishers, edition labels, decorative text, and ISBN numbers.
Infer the book language from context clues in the text.

OCR Text:
{ocr_text}

Extract:
- Title: The main book title (without subtitles)
- Author: The primary author's name
- Language: Use language code (eng, fre, ger, spa, ita, etc.)
"""

        logger.debug("Sending prompt to LLM for parsing")
        result = structured_llm.invoke(prompt)

        if not result:
            logger.warning("LLM returned empty result")
            return None

        logger.info(
            "Parsed metadata - Title: %s, Author: %s, Language: %s",
            result.title,
            result.author,
            result.language,
        )
        logger.debug("Full parsed metadata: %s", result)

        return result

    except ValueError:
        raise
    except Exception as e:
        logger.error("Book metadata parsing failed: %s", e)
        raise
