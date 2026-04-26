"""
Clusterer - UMAP + HDBSCAN to group reviews by semantic similarity.
"""
import logging
import numpy as np
import umap
import hdbscan

logger = logging.getLogger(__name__)

def cluster_embeddings(embeddings: list[list[float]], min_cluster_size: int = 5) -> list[int]:
    """
    Cluster embeddings using UMAP for dimensionality reduction and HDBSCAN for clustering.
    Returns a list of cluster labels (-1 is noise).
    """
    if not embeddings:
        return []
    
    n_samples = len(embeddings)
    if n_samples < min_cluster_size:
        logger.warning("Not enough samples to cluster (min %d, got %d). Falling back to single cluster.", min_cluster_size, n_samples)
        # All in cluster 0
        return [0] * n_samples

    X = np.array(embeddings)
    
    # UMAP dimensionality reduction
    n_components = min(5, n_samples - 2)
    n_neighbors = min(15, n_samples - 1)
    
    if n_components < 2:
        # Too few samples for UMAP, skip it
        X_reduced = X
    else:
        logger.info("Reducing dimensions with UMAP (n_neighbors=%d, n_components=%d)", n_neighbors, n_components)
        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            n_components=n_components,
            metric='cosine',
            random_state=42
        )
        X_reduced = reducer.fit_transform(X)

    # HDBSCAN clustering
    logger.info("Clustering with HDBSCAN (min_cluster_size=%d)", min_cluster_size)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    labels = clusterer.fit_predict(X_reduced)
    
    # Check if all noise
    if all(l == -1 for l in labels):
        logger.warning("HDBSCAN labeled all points as noise. Falling back to single cluster.")
        return [0] * n_samples
        
    return labels.tolist()
