import time
import pytest
import numpy as np
from app.services.pdf_parser import extract_text_from_pdf, extract_pdfs_from_zip
from app.services.embedding_service import (
    get_text_embedding,
    serialize_embedding,
    deserialize_embedding,
    rank_precomputed_vector_candidates
)

def test_embedding_serialization():
    vec = get_text_embedding("Senior Python Developer with 5 years experience in FastAPI and React")
    assert isinstance(vec, np.ndarray)
    assert len(vec) == 384 or len(vec) == 768

    json_str = serialize_embedding(vec)
    assert isinstance(json_str, str)

    restored = deserialize_embedding(json_str)
    assert restored is not None
    assert np.allclose(vec, restored, atol=1e-5)

def test_precomputed_vector_ranking_performance():
    """
    Simulates screening 500 candidates against 1 Job Description using pre-computed vectors.
    Measures matrix similarity ranking speed.
    """
    job_desc = "Software Engineer specialized in Python, FastAPI, Docker and PostgreSQL"
    dummy_vec = get_text_embedding(job_desc)
    dummy_json = serialize_embedding(dummy_vec)

    resumes = [
        (f"candidate_{i}", f"Resume candidate {i} with Python experience", dummy_json)
        for i in range(500)
    ]

    # Warmup model encoding
    _ = rank_precomputed_vector_candidates(job_desc, resumes[:1])

    start_time = time.perf_counter()
    rankings = rank_precomputed_vector_candidates(job_desc, resumes)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    assert len(rankings) == 500
    assert rankings[0][1] >= 90.0
    print(f"\n[BENCHMARK] Ranked 500 candidates with pre-computed vectors in {elapsed_ms:.2f} ms")
    assert elapsed_ms < 200.0  # Under 200ms threshold for CPU environment
