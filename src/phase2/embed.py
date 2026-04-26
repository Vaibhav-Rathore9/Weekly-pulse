"""
Embedder - vectorise text using sentence-transformers (local) or litellm.
"""
import os
import logging

logger = logging.getLogger(__name__)

# Default model, can be overridden by env
DEFAULT_EMBEDDING_MODEL = "local/all-MiniLM-L6-v2"

# Global lazy-loaded local model
_LOCAL_EMBEDDER = None

def get_embeddings(texts: list[str], model: str = None) -> list[list[float]]:
    """
    Get embeddings for a list of texts.
    If model starts with 'local/', it uses sentence-transformers.
    Otherwise uses litellm.
    """
    model = model or os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    
    if not texts:
        return []
    
    logger.info("Generating embeddings for %d texts using %s", len(texts), model)
    
    if model.startswith("local/"):
        model_name = model.replace("local/", "")
        global _LOCAL_EMBEDDER
        if _LOCAL_EMBEDDER is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading local embedding model: %s", model_name)
            _LOCAL_EMBEDDER = SentenceTransformer(model_name)
            
        embeddings = _LOCAL_EMBEDDER.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
        
    else:
        from litellm import embedding
        try:
            # litellm embedding supports batching
            response = embedding(model=model, input=texts)
            # return list of embeddings in the same order
            embeddings = [data['embedding'] for data in response.data]
            return embeddings
        except Exception as e:
            logger.error("Failed to generate embeddings via litellm: %s", e)
            raise
