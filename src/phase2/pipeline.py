"""
Phase 2 Pipeline - Connects PII Scrubbing, Embedding, Clustering, and LLM Reasoning.
"""
import logging
import pandas as pd
from .pii import scrub_pii
from .embed import get_embeddings
from .cluster import cluster_embeddings
from .llm import generate_theme_insights
from .validator import validate_quotes

logger = logging.getLogger(__name__)

def process_reviews(df: pd.DataFrame) -> dict:
    """
    Process normalized reviews and return structured insights JSON.
    """
    if df.empty:
        logger.warning("Empty dataframe provided to process_reviews.")
        return {"themes": []}
        
    logger.info("Starting Phase 2 processing for %d reviews", len(df))
    
    # 1. PII Scrubbing
    scrubbed_texts = []
    original_texts = []
    review_ids = []
    
    for _, row in df.iterrows():
        text = row['text']
        original_texts.append(text)
        review_ids.append(row['review_id'])
        
        scrubbed, _ = scrub_pii(text)
        scrubbed_texts.append(scrubbed)
        
    # 2. Embedding
    embeddings = get_embeddings(scrubbed_texts)
    
    # 3. Clustering
    labels = cluster_embeddings(embeddings)
    
    # Group reviews by cluster
    clusters = {}
    for i, label in enumerate(labels):
        if label == -1:
            continue # Skip noise
        if label not in clusters:
            clusters[label] = []
        clusters[label].append({
            'review_id': review_ids[i],
            'text': scrubbed_texts[i],
            'original_text': original_texts[i]
        })
        
    logger.info("Found %d clusters (excluding noise)", len(clusters))
    
    # 4 & 5. LLM Reasoning & Quote Validation
    themes = []
    
    for label, cluster_reviews in clusters.items():
        # Limit to 50 reviews per cluster to fit context window
        sample_reviews = cluster_reviews[:50]
        
        insights = generate_theme_insights(sample_reviews)
        if not insights:
            continue
            
        quotes = insights.get('quotes', [])
        
        # Original texts for this cluster
        cluster_original_texts = [r['original_text'] for r in cluster_reviews]
        
        valid_quotes = validate_quotes(quotes, cluster_original_texts)
        
        if not valid_quotes and quotes:
            logger.warning("All quotes failed validation for cluster %s", insights.get('name'))
            
        themes.append({
            'name': insights.get('name', f"Theme {label}"),
            'quotes': valid_quotes,
            'action_idea': insights.get('action_idea', ""),
            'review_count': len(cluster_reviews)
        })
        
    # Sort themes by review count descending
    themes.sort(key=lambda x: x['review_count'], reverse=True)
    
    logger.info("Successfully extracted %d themes", len(themes))
    
    return {"themes": themes}
