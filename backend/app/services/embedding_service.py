import numpy as np
from typing import List, Tuple

try:
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _model = None

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
    resumes: List[Tuple[str, str]] # List of (resume_id, raw_text)
) -> List[Tuple[str, float]]:
    """
    Ranks candidates using vector cosine similarity.
    Returns sorted list of (resume_id, similarity_score_0_to_100).
    """
    if not resumes:
        return []

    if _model is not None:
        jd_emb = get_text_embedding(job_description_text)
        results = []
        for resume_id, text in resumes:
            res_emb = get_text_embedding(text)
            sim = compute_cosine_similarity(jd_emb, res_emb)
            score = round(max(0.0, min(100.0, sim * 100.0)), 2)
            results.append((resume_id, score))
    else:
        results = []
        for resume_id, text in resumes:
            sim = fallback_keyword_similarity(job_description_text, text)
            score = round(max(0.0, min(100.0, sim * 100.0)), 2)
            results.append((resume_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
