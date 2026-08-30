import logging
import numpy as np
from typing import List, Tuple

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("SentenceTransformer 'all-MiniLM-L6-v2' loaded successfully.")
except Exception:
    _model = None
    logger.warning("SentenceTransformer unavailable. Falling back to keyword similarity.")

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def fallback_keyword_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return float(len(intersection) / len(union))

def get_text_embedding(text: str) -> np.ndarray:
    if _model is not None:
        return _model.encode(text, convert_to_numpy=True)
    return np.zeros(384)

def rank_candidates_by_vector_similarity(
    job_description_text: str,
    resumes: List[Tuple[str, str]]  # List of (resume_id, raw_text)
) -> List[Tuple[str, float]]:
    """
    Ranks candidates using vector cosine similarity with batch encoding.
    Returns sorted list of (resume_id, similarity_score_0_to_100).

    Optimization: Uses batch encode for all resume texts in a single call,
    then vectorized numpy cosine similarity instead of per-CV sequential encoding.
    """
    if not resumes:
        return []

    resume_ids = [rid for rid, _ in resumes]
    resume_texts = [text for _, text in resumes]

    if _model is not None:
        # Batch encode: single call encodes all texts at once (GPU/CPU batched)
        jd_emb = _model.encode(job_description_text, convert_to_numpy=True)
        resume_embeddings = _model.encode(
            resume_texts,
            batch_size=64,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        # Vectorized cosine similarity: jd_emb (1, D) vs resume_embeddings (N, D)
        jd_norm = jd_emb / (np.linalg.norm(jd_emb) + 1e-10)
        resume_norms = resume_embeddings / (np.linalg.norm(resume_embeddings, axis=1, keepdims=True) + 1e-10)
        similarities = np.dot(resume_norms, jd_norm)  # shape: (N,)

        results = [
            (rid, round(max(0.0, min(100.0, float(sim) * 100.0)), 2))
            for rid, sim in zip(resume_ids, similarities)
        ]
    else:
        # Fallback: keyword-based Jaccard similarity
        results = [
            (rid, round(max(0.0, min(100.0, fallback_keyword_similarity(job_description_text, text) * 100.0)), 2))
            for rid, text in resumes
        ]

    results.sort(key=lambda x: x[1], reverse=True)
    return results

