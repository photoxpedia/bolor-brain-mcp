"""
Embedding Service for Semantic Memory
=====================================
Uses all-mpnet-base-v2 for high-quality 768-dim embeddings.
Singleton pattern with lazy loading for efficiency.
"""
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton embedding service with lazy loading.

    Uses all-mpnet-base-v2 model which provides:
    - 768 dimensional embeddings
    - High quality semantic representations
    - Good balance of quality and speed
    """

    _instance = None
    _model = None
    MODEL_NAME = "all-mpnet-base-v2"
    EMBEDDING_DIM = 768

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        """Lazy load the embedding model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.MODEL_NAME}")
                self._model = SentenceTransformer(self.MODEL_NAME)
                logger.info(f"Embedding model loaded successfully ({self.EMBEDDING_DIM} dimensions)")
            except ImportError:
                logger.warning("sentence-transformers not installed. Embeddings disabled.")
                self._model = None
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self._model = None

    def is_available(self) -> bool:
        """Check if embedding service is available"""
        self._load_model()
        return self._model is not None

    def encode(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding, or None if failed
        """
        self._load_model()
        if self._model is None:
            return None

        if not text or not text.strip():
            return None

        try:
            embedding = self._model.encode([text], show_progress_bar=False)[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for encoding

        Returns:
            List of embeddings (None for any that failed)
        """
        self._load_model()
        if self._model is None:
            return [None] * len(texts)

        if not texts:
            return []

        try:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                # Filter empty texts
                valid_indices = [j for j, t in enumerate(batch) if t and t.strip()]
                valid_texts = [batch[j] for j in valid_indices]

                if valid_texts:
                    batch_emb = self._model.encode(valid_texts, show_progress_bar=False)

                    # Map back to original positions
                    result = [None] * len(batch)
                    for idx, emb in zip(valid_indices, batch_emb):
                        result[idx] = emb.tolist()
                    embeddings.extend(result)
                else:
                    embeddings.extend([None] * len(batch))

            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [None] * len(texts)

    @staticmethod
    def cosine_similarity(emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            emb1: First embedding vector
            emb2: Second embedding vector

        Returns:
            Cosine similarity score between -1 and 1
        """
        if emb1 is None or emb2 is None:
            return 0.0

        try:
            a = np.array(emb1)
            b = np.array(emb2)

            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            return float(np.dot(a, b) / (norm_a * norm_b))
        except Exception:
            return 0.0

    @staticmethod
    def euclidean_distance(emb1: List[float], emb2: List[float]) -> float:
        """
        Calculate Euclidean distance between two embeddings.

        Args:
            emb1: First embedding vector
            emb2: Second embedding vector

        Returns:
            Euclidean distance (lower = more similar)
        """
        if emb1 is None or emb2 is None:
            return float('inf')

        try:
            a = np.array(emb1)
            b = np.array(emb2)
            return float(np.linalg.norm(a - b))
        except Exception:
            return float('inf')

    def find_most_similar(self, query_embedding: List[float],
                         candidate_embeddings: List[List[float]],
                         top_k: int = 5) -> List[tuple]:
        """
        Find the most similar embeddings to a query.

        Args:
            query_embedding: The query embedding
            candidate_embeddings: List of candidate embeddings to compare
            top_k: Number of top results to return

        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if query_embedding is None or not candidate_embeddings:
            return []

        similarities = []
        for i, emb in enumerate(candidate_embeddings):
            if emb is not None:
                sim = self.cosine_similarity(query_embedding, emb)
                similarities.append((i, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]


# Global singleton instance
embedding_service = EmbeddingService()
