"""
Demo: Matching engine cho CV-JD.
Nhan input la JSON CV da trich xuat (tu buoc LLM extraction truoc do)
va danh sach JD, tra ve top-k JD phu hop nhat bang KNN + cosine similarity
tren embedding ngu nghia.

Yeu cau:
    pip install sentence-transformers scikit-learn numpy

Neu chua cai sentence-transformers (thu vien nay khá nang, can tai model
~400MB lan dau), script se tu dong fallback ve TF-IDF de ban van test duoc
logic matching ngay, sau do nang cap embedding sau khong can sua code khac.

Cach chay:
    python cv_jd_matching.py cv_extracted.json
    python cv_jd_matching.py cv_extracted.json --jd-file jds.json --top-k 3
"""

import argparse
import json
import sys
from typing import List, Dict, Any

import numpy as np
from sklearn.neighbors import NearestNeighbors

# --- Du lieu JD mau de demo khi chua co du lieu that ---
SAMPLE_JDS = [
    {
        "job_id": "jd001",
        "title": "Backend Developer (Python)",
        "required_skills": ["Python", "Flask", "PostgreSQL", "Docker", "REST API"],
        "description": "Phat trien va toi uu API backend, lam viec voi co so du lieu quan he, "
                        "trien khai dich vu bang Docker, phoi hop voi team frontend.",
        "min_experience_years": 1,
    },
    {
        "job_id": "jd002",
        "title": "Data Analyst",
        "required_skills": ["SQL", "Python", "Power BI", "Excel", "Thong ke"],
        "description": "Phan tich du lieu kinh doanh, xay dung bao cao, truc quan hoa du lieu "
                        "cho ban lanh dao ra quyet dinh.",
        "min_experience_years": 0,
    },
    {
        "job_id": "jd003",
        "title": "Frontend Developer (React)",
        "required_skills": ["JavaScript", "React", "HTML", "CSS", "Git"],
        "description": "Xay dung giao dien nguoi dung bang ReactJS, toi uu hieu nang, "
                        "phoi hop voi backend qua REST API.",
        "min_experience_years": 1,
    },
    {
        "job_id": "jd004",
        "title": "DevOps Engineer",
        "required_skills": ["Docker", "Kubernetes", "CI/CD", "Linux", "AWS"],
        "description": "Xay dung va van hanh he thong CI/CD, quan ly ha tang cloud, "
                        "dam bao he thong hoat dong on dinh.",
        "min_experience_years": 2,
    },
    {
        "job_id": "jd005",
        "title": "QA/Tester",
        "required_skills": ["Manual Testing", "Selenium", "SQL", "Test case design"],
        "description": "Kiem thu phan mem, viet test case, phat hien va bao cao loi, "
                        "phoi hop voi dev de dam bao chat luong san pham.",
        "min_experience_years": 0,
    },
]


# --- Lop embedding: uu tien sentence-transformers, fallback TF-IDF neu chua cai ---

class Embedder:
    def __init__(self):
        self.backend = None
        self.model = None
        self._vectorizer = None
        self._try_load_sentence_transformer()

    def _try_load_sentence_transformer(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Model da ngon ngu, ho tro tot tieng Viet, kich thuoc nho (~470MB)
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            self.backend = "sentence-transformers"
        except Exception as e:
            print(f"[Canh bao] Khong tai duoc sentence-transformers ({e}).", file=sys.stderr)
            print("           -> Dung TF-IDF tam thoi de test logic matching.", file=sys.stderr)
            print("           -> Cai dat: pip install sentence-transformers", file=sys.stderr)
            self.backend = "tfidf"

    def fit_and_encode_corpus(self, texts: List[str]) -> np.ndarray:
        """Dung khi can fit tren toan bo corpus truoc (bat buoc voi TF-IDF)."""
        if self.backend == "sentence-transformers":
            return self.model.encode(texts, normalize_embeddings=True)
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer()
            matrix = self._vectorizer.fit_transform(texts)
            return matrix.toarray()

    def encode(self, texts: List[str]) -> np.ndarray:
        """Dung sau khi da fit (voi TF-IDF) hoac bat ky luc nao (voi sentence-transformers)."""
        if self.backend == "sentence-transformers":
            return self.model.encode(texts, normalize_embeddings=True)
        else:
            if self._vectorizer is None:
                raise RuntimeError("TF-IDF chua duoc fit. Goi fit_and_encode_corpus() truoc.")
            return self._vectorizer.transform(texts).toarray()


# --- Xay dung text co trong so tu du lieu da trich xuat ---

def build_cv_text(cv_data: Dict[str, Any]) -> str:
    """Ghep text CV co trong so: ky nang duoc nhan doi vi la tin hieu quan trong nhat."""
    skills = cv_data.get("skills", [])
    work_desc = " ".join(
        f"{w.get('position', '')} {w.get('description', '')}"
        for w in cv_data.get("work_experience", [])
    )
    skills_text = " ".join(skills)
    # Nhan doi phan skills de tang trong so trong embedding
    return f"{skills_text} {skills_text} {work_desc}"


def build_jd_text(jd: Dict[str, Any]) -> str:
    skills_text = " ".join(jd.get("required_skills", []))
    return f"{jd.get('title', '')} {skills_text} {skills_text} {jd.get('description', '')}"


# --- Matching engine: KNN + cosine ---

def match_cv_to_jds(cv_vector: np.ndarray, jd_vectors: np.ndarray, jd_list: List[Dict], top_k: int = 3):
    n_neighbors = min(top_k, len(jd_list))
    knn = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
    knn.fit(jd_vectors)

    distances, indices = knn.kneighbors(cv_vector.reshape(1, -1))

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        similarity = 1 - dist  # cosine distance -> cosine similarity
        jd = jd_list[idx]
        results.append({
            "job_id": jd["job_id"],
            "title": jd["title"],
            "similarity_score": round(float(similarity), 4),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Matching engine: xep hang JD phu hop voi CV")
    parser.add_argument("cv_file", help="File JSON CV da trich xuat (tu buoc LLM extraction)")
    parser.add_argument("--jd-file", default=None, help="File JSON danh sach JD (mac dinh dung du lieu mau)")
    parser.add_argument("--top-k", type=int, default=3, help="So luong JD phu hop nhat can tra ve")
    args = parser.parse_args()

    with open(args.cv_file, "r", encoding="utf-8") as f:
        cv_data = json.load(f)

    if args.jd_file:
        with open(args.jd_file, "r", encoding="utf-8") as f:
            jd_list = json.load(f)
    else:
        print("[Thong bao] Khong co --jd-file, dung 5 JD mau de demo.")
        jd_list = SAMPLE_JDS

    print("[1/3] Dang khoi tao embedder ...")
    embedder = Embedder()
    print(f"      -> Dang dung backend: {embedder.backend}")

    print("[2/3] Dang vector hoa CV va JD ...")
    jd_texts = [build_jd_text(jd) for jd in jd_list]
    cv_text = build_cv_text(cv_data)

    # Voi TF-IDF: bat buoc fit tren toan bo corpus (JD + CV) truoc de cung khong gian vector
    if embedder.backend == "tfidf":
        all_texts = jd_texts + [cv_text]
        all_vectors = embedder.fit_and_encode_corpus(all_texts)
        jd_vectors = all_vectors[:-1]
        cv_vector = all_vectors[-1]
    else:
        jd_vectors = embedder.encode(jd_texts)
        cv_vector = embedder.encode([cv_text])[0]

    print("[3/3] Dang xep hang bang KNN + cosine similarity ...")
    results = match_cv_to_jds(cv_vector, jd_vectors, jd_list, top_k=args.top_k)

    print("\nKet qua top JD phu hop nhat:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['job_id']}] {r['title']} - do phu hop: {r['similarity_score']}")


if __name__ == "__main__":
    main()
