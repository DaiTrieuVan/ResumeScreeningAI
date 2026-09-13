# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

import json
import logging
import os
import numpy as np
from typing import List, Tuple, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_model = None
_model_load_attempted = False


def _get_model():
    """Load the optional transformer only when an embedding is first requested.

    Importing the FastAPI application must remain cheap and deterministic. This
    also lets automated tests explicitly exercise the keyword fallback without
    downloading or initializing a large model during test discovery.
    """
    global _model, _model_load_attempted
    if _model_load_attempted or os.getenv("DISABLE_EMBEDDING_MODEL", "").lower() in {"1", "true", "yes"}:
        return _model
    _model_load_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        try:
            _model = SentenceTransformer(settings.DEFAULT_EMBEDDING_MODEL)
        except Exception:
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer loaded successfully.")
    except Exception as error:
        _model = None
        logger.warning("SentenceTransformer unavailable: %s. Falling back to keyword similarity.", error)
    return _model

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
    model = _get_model()
    if model is not None and text:
        return model.encode(text, convert_to_numpy=True)
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

    model = _get_model()
    if model is None:
        results = [
            (rid, round(max(0.0, min(100.0, fallback_keyword_similarity(job_description_text, raw_text) * 100.0)), 2))
            for rid, raw_text, _ in resumes
        ]
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # Encode Job Description
    jd_emb = model.encode(job_description_text, convert_to_numpy=True)
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
        new_embs = model.encode(missing_texts, batch_size=64, convert_to_numpy=True, show_progress_bar=False)
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

