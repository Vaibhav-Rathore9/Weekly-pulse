"""
Delivery Module - Connects to the external MCP (REST) server on Render.
"""
import logging
import requests
from ..config import load_config

logger = logging.getLogger(__name__)

def deliver_report(product: str, doc_id: str, stakeholder_emails: list[str], markdown_content: str, email_html: str, email_subject: str):
    """
    Delivers the report by appending to a Google Doc and sending a Gmail draft via the Render MCP server.
    """
    config = load_config()
    server_url = config.get("delivery", {}).get("mcp_server_url")
    
    if not server_url:
        raise ValueError("MCP server URL not found in config.yaml")
        
    # 1. Append to Google Doc
    logger.info("Delivering to Google Doc (ID: %s) via %s/append_to_doc", doc_id, server_url)
    try:
        doc_response = requests.post(
            f"{server_url}/append_to_doc",
            json={
                "doc_id": doc_id,
                "content": markdown_content
            },
            timeout=30
        )
        doc_response.raise_for_status()
        logger.info("Successfully appended to Google Doc.")
    except Exception as e:
        logger.error("Failed to deliver to Google Doc: %s", e)
        raise

    # 2. Create Gmail Draft
    # We'll send to the first stakeholder as a primary recipient for now
    if not stakeholder_emails:
        logger.warning("No stakeholder emails configured. Skipping email delivery.")
        return
        
    recipient = stakeholder_emails[0]
    logger.info("Creating Gmail draft for %s via %s/create_email_draft", recipient, server_url)
    
    try:
        email_response = requests.post(
            f"{server_url}/create_email_draft",
            json={
                "to": recipient,
                "subject": email_subject,
                "body": email_html
            },
            timeout=30
        )
        email_response.raise_for_status()
        logger.info("Successfully created Gmail draft.")
    except Exception as e:
        logger.error("Failed to create Gmail draft: %s", e)
        # We don't necessarily want to fail the whole run if email fails but doc succeeded,
        # but for now we raise to be safe.
        raise
