"""
Report Renderer - applies Jinja2 templates to Phase 2 output to generate Markdown and HTML/Text emails.
"""
import os
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# Set up Jinja2 environment pointing to the templates directory
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

def render_markdown(product: str, iso_week: str, total_reviews: int, themes: list[dict]) -> str:
    """Render the Google Docs Markdown template."""
    logger.info("Rendering markdown doc for %s / %s", product, iso_week)
    template = env.get_template("doc_template.md.j2")
    return template.render(
        product=product,
        iso_week=iso_week,
        total_reviews=total_reviews,
        themes=themes
    )

def render_email(product: str, iso_week: str, total_reviews: int, themes: list[dict], doc_url: str) -> tuple[str, str, str]:
    """
    Render the email content.
    Returns: (subject, html_body, text_body)
    """
    logger.info("Rendering email for %s / %s", product, iso_week)
    
    subject = f"[{product.title()}] Weekly Review Pulse - {iso_week}"
    
    html_template = env.get_template("email_template.html.j2")
    html_body = html_template.render(
        product=product,
        iso_week=iso_week,
        total_reviews=total_reviews,
        themes=themes,
        doc_url=doc_url
    )
    
    text_template = env.get_template("email_template.txt.j2")
    text_body = text_template.render(
        product=product,
        iso_week=iso_week,
        total_reviews=total_reviews,
        themes=themes,
        doc_url=doc_url
    )
    
    return subject, html_body, text_body
