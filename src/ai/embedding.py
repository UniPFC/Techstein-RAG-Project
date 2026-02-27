"""
Embedding engine for generating vector representations of text.
Adapted from SoulsborneRAG for multi-tenant chat system.
"""

from typing import List
from config.logger import logger
from src.ai.provider.base import EmbeddingProvider


class EmbeddingEngine:
    """
    Orchestrates embedding generation.
    Abstracts the provider layer for higher-level RAG operations.
    """
    
    def __init__(self, provider: EmbeddingProvider):
        """
        Initialize with an embedding provider.
        
        Args:
            provider: EmbeddingProvider instance (HFEmbeddingProvider or RemoteEmbeddingProvider)
        """
        self.provider = provider
        logger.info("EmbeddingEngine initialized")
    
    def embed(self, inputs: List[str], **kwargs) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            inputs: List of text strings
            **kwargs: Provider-specific parameters
            
        Returns:
            List of embedding vectors
        """
        logger.debug(f"Embedding {len(inputs)} inputs")
        embeddings = self.provider.embed(inputs, **kwargs)
        return embeddings
    
    def embed_single(self, text: str, **kwargs) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            **kwargs: Provider-specific parameters
            
        Returns:
            Single embedding vector
        """
        return self.embed([text], **kwargs)[0]
