"""
PII Scrubber - redact phone numbers, emails, and URLs from review text.
"""
import re

# Simple regex patterns for PII
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b')
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
URL_REGEX = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

def scrub_pii(text: str) -> tuple[str, dict]:
    """
    Scrub PII from text and return the scrubbed text and a report.
    """
    emails_found = len(EMAIL_REGEX.findall(text))
    text = EMAIL_REGEX.sub('[EMAIL]', text)
    
    phones_found = len(PHONE_REGEX.findall(text))
    text = PHONE_REGEX.sub('[PHONE]', text)
    
    urls_found = len(URL_REGEX.findall(text))
    text = URL_REGEX.sub('[URL]', text)
    
    report = {
        'emails_found': emails_found,
        'phones_found': phones_found,
        'urls_found': urls_found
    }
    
    return text, report
