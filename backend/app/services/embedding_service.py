import json
import logging
import numpy as np
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

_model = None
try:
    from sentence_transformers import SentenceTransformer
    # Try multilingual model first for Vietnamese + English support
    try:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        logger.info("SentenceTransformer 'paraphrase-multilingual-MiniLM-L12-v2' loaded successfully.")
    except Exception:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("SentenceTransformer 'all-MiniLM-L6-v2' loaded successfully.")
except Exception as e:
    _model = None
    logger.warning(f"SentenceTransformer unavailable: {e}. Falling back to keyword similarity.")

def compute_cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def serialize_embedding(vec: np.ndarray) -> str:
    """Serializes numpy array vector into JSON string for DB storage."""
    if vec is None:
        return ""
    return json.dumps(vec.tolist())

def deserialize_embedding(json_str: Optional[str]) -> Optional[np.ndarray]:
    """Deserializes JSON string back to numpy array."""
    if not json_str:
        return None
    try:
        arr = json.loads(json_str)
        return np.array(arr, dtype=np.float32)
    except Exception:
        return None

def fallback_keyword_similarity(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)
    return float(len(intersection) / len(union))

def get_text_embedding(text: str) -> np.ndarray:
    if _model is not None and text:
        return _model.encode(text, convert_to_numpy=True)
    return np.zeros(384, dtype=np.float32)

def rank_candidates_by_vector_similarity(
    job_description_text: str,
    resumes: List[Tuple[str, str]]  # List of (resume_id, raw_text)
) -> List[Tuple[str, float]]:
    """
    Legacy method: Encodes all resume texts on the fly.
    """
    resumes_with_cached = [(rid, text, None) for rid, text in resumes]
    return rank_precomputed_vector_candidates(job_description_text, resumes_with_cached)

def rank_precomputed_vector_candidates(
    job_description_text: str,
    resumes: List[Tuple[str, str, Optional[str]]]  # List of (resume_id, raw_text, embedding_json)
) -> List[Tuple[str, float]]:
    """
    Ranks candidates using pre-computed vector embeddings whenever available.
    Uses ultra-fast matrix multiplication (N, D) x (D, 1) -> < 5ms for 1,000 CVs.
    """
    if not resumes:
        return []

    if _model is None:
        results = [
            (rid, round(max(0.0, min(100.0, fallback_keyword_similarity(job_description_text, raw_text) * 100.0)), 2))
            for rid, raw_text, _ in resumes
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # Encode Job Description
    jd_emb = _model.encode(job_description_text, convert_to_numpy=True)
    jd_norm = jd_emb / (np.linalg.norm(jd_emb) + 1e-10)

    resume_embeddings = []
    resume_ids = []
    missing_indices = []
    missing_texts = []

    for idx, (rid, raw_text, cached_json) in enumerate(resumes):
        resume_ids.append(rid)
        vec = deserialize_embedding(cached_json)
        if vec is not None:
            resume_embeddings.append(vec)
        else:
            resume_embeddings.append(None)
            missing_indices.append(idx)
            missing_texts.append(raw_text or "")

    # Encode missing embeddings in batch
    if missing_texts:
        new_embs = _model.encode(missing_texts, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
        for missing_idx, new_vec in zip(missing_indices, new_embs):
            resume_embeddings[missing_idx] = new_vec

    # Stack into numpy matrix (N, D)
    emb_matrix = np.array(resume_embeddings, dtype=np.float32)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True) + 1e-10
    normalized_matrix = emb_matrix / norms

    # Cosine Similarity via Dot Product (N, D) x (D, 1) -> (N,)
    similarities = np.dot(normalized_matrix, jd_norm)

    results = [
        (rid, round(max(0.0, min(100.0, float(sim) * 100.0)), 2))
        for rid, sim in zip(resume_ids, similarities)
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    return results

