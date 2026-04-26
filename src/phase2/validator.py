"""
Quote Validator - ensure LLM-extracted quotes exist in the original text.
"""
import logging
import re

logger = logging.getLogger(__name__)

def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace for easier comparison."""
    return re.sub(r'\s+', ' ', text).strip().lower()

def validate_quote(quote: str, original_texts: list[str]) -> tuple[bool, str | None]:
    """
    Check if the quote is a literal substring of any original text.
    Returns (is_valid, matching_original_text_if_any)
    """
    norm_quote = _normalize_whitespace(quote)
    if not norm_quote:
        return False, None
        
    for text in original_texts:
        norm_text = _normalize_whitespace(text)
        if norm_quote in norm_text:
            return True, text
            
    return False, None

def validate_quotes(quotes: list[dict], original_texts: list[str]) -> list[dict]:
    """
    Validates a list of quotes. Discards invalid ones.
    quote dict format: {'text': '...', 'review_id': '...'}
    """
    valid_quotes = []
    
    for q in quotes:
        quote_text = q.get('text', '')
        if not quote_text:
            continue
            
        is_valid, _ = validate_quote(quote_text, original_texts)
        if is_valid:
            valid_quotes.append(q)
        else:
            logger.debug("Quote validation failed. Quote: %s", quote_text)
            
    return valid_quotes
