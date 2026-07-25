"""
Tang 2 cua kien truc matching: LLM Rerank + Explainability.

Kien truc 2 tang:
    Tang 1 (retrieval - dien rong, toc do cao):
        cv_jd_matching.py  ->  embedding + KNN cosine  ->  top N JD gan nhat (vi du N=20)
    Tang 2 (rerank - dien hep, can do chinh xac cao)  <-- FILE NAY:
        top N JD  ->  Gemini cham lai diem + giai thich  ->  top K JD cuoi cung (vi du K=3)

Ly do tach 2 tang: goi LLM cho TOAN BO JD se qua cham/dat (vi du 100 CV x 500 JD
= 50.000 lan goi). Chi goi LLM tren tap da duoc thu hep boi embedding giup
so lan goi LLM giam xuong con vai chuc, van dam bao toc do va chi phi hop ly.

Yeu cau:
    pip install google-genai
    Set bien moi truong GEMINI_API_KEY (xem cv_extract_gemini.py)

Cach chay (doc lap, dung du lieu mau):
    python cv_jd_rerank.py sample_cv_extracted.json

Cach chay noi tiep tu cv_jd_matching.py (khuyen dung):
    python cv_jd_rerank.py sample_cv_extracted.json --retrieve-top-n 20 --final-top-k 3
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Tai su dung lai logic tang 1 tu file matching da co, tranh trung lap code
from cv_jd_matching import (
    SAMPLE_JDS,
    Embedder,
    build_cv_text,
    build_jd_text,
    match_cv_to_jds,
)

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """Ban la chuyen gia tuyen dung, danh gia muc do phu hop giua
mot ho so ung vien (CV) va mot mo ta cong viec (JD).

QUY TAC BAT BUOC:
- Chi danh gia dua tren ky nang, kinh nghiem, hoc van CO TRONG du lieu duoc cung cap.
- KHONG suy doan hay danh gia dua tren ten, gioi tinh, tuoi tac, ngoai hinh.
- Diem so tu 0 den 100, phan anh muc do phu hop thuc te ve chuyen mon.
- Giai thich ngan gon (1-2 cau), neu ro ky nang/kinh nghiem nao khop va thieu gi."""


class RerankResult(BaseModel):
    job_id: str = Field(description="ID cua JD dang duoc danh gia")
    match_score: int = Field(description="Diem phu hop tu 0 den 100")
    matched_points: List[str] = Field(
        default_factory=list, description="Cac ky nang/kinh nghiem CV co va JD yeu cau, da khop"
    )
    missing_points: List[str] = Field(
        default_factory=list, description="Cac yeu cau cua JD ma CV con thieu"
    )
    explanation: str = Field(description="Giai thich ngan gon 1-2 cau vi sao co diem so nay")


class RerankResponse(BaseModel):
    results: List[RerankResult]


def build_rerank_prompt(cv_data: Dict[str, Any], shortlisted_jds: List[Dict[str, Any]]) -> str:
    """Ghep CV va danh sach JD da duoc thu hep (tu tang 1) thanh 1 prompt duy nhat,
    de LLM cham diem toan bo trong 1 lan goi thay vi goi rieng tung cap (tiet kiem chi phi)."""
    cv_summary = {
        "skills": cv_data.get("skills", []),
        "work_experience": [
            {"position": w.get("position"), "description": w.get("description")}
            for w in cv_data.get("work_experience", [])
        ],
        "education": cv_data.get("education", []),
    }

    jd_summaries = [
        {
            "job_id": jd["job_id"],
            "title": jd["title"],
            "required_skills": jd.get("required_skills", []),
            "description": jd.get("description", ""),
        }
        for jd in shortlisted_jds
    ]

    return f"""Ho so ung vien (CV):
{json.dumps(cv_summary, ensure_ascii=False, indent=2)}

Danh sach cong viec can danh gia (JD):
{json.dumps(jd_summaries, ensure_ascii=False, indent=2)}

Hay cham diem phu hop cho TUNG JD trong danh sach tren dua tren ho so ung vien."""


def rerank_with_llm(
    cv_data: Dict[str, Any],
    shortlisted_jds: List[Dict[str, Any]],
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Goi Gemini MOT LAN DUY NHAT de cham diem toan bo danh sach JD da rut gon."""
    client = genai.Client(api_key=api_key)

    prompt = build_rerank_prompt(cv_data, shortlisted_jds)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=RerankResponse,
            temperature=0,
        ),
    )
    parsed = json.loads(response.text)
    return parsed["results"]


def retrieve_then_rerank(
    cv_data: Dict[str, Any],
    jd_list: List[Dict[str, Any]],
    api_key: str,
    retrieve_top_n: int = 10,
    final_top_k: int = 3,
    model: str = DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Ham chinh: chay tron ven ca 2 tang.
    Tang 1: embedding + KNN cosine -> loc nhanh top N JD.
    Tang 2: LLM rerank -> cham diem lai + giai thich -> chon top K cuoi cung."""

    # --- Tang 1: Retrieval (nhanh, dien rong) ---
    print(f"[Tang 1] Dang loc nhanh top {retrieve_top_n} JD bang embedding + KNN ...")
    embedder = Embedder()
    print(f"         -> Dung backend: {embedder.backend}")

    jd_texts = [build_jd_text(jd) for jd in jd_list]
    cv_text = build_cv_text(cv_data)

    if embedder.backend == "tfidf":
        all_vectors = embedder.fit_and_encode_corpus(jd_texts + [cv_text])
        jd_vectors, cv_vector = all_vectors[:-1], all_vectors[-1]
    else:
        jd_vectors = embedder.encode(jd_texts)
        cv_vector = embedder.encode([cv_text])[0]

    retrieved = match_cv_to_jds(cv_vector, jd_vectors, jd_list, top_k=retrieve_top_n)
    retrieved_ids = {r["job_id"] for r in retrieved}
    shortlisted_jds = [jd for jd in jd_list if jd["job_id"] in retrieved_ids]
    print(f"         -> Da rut gon tu {len(jd_list)} xuong con {len(shortlisted_jds)} JD.")

    # --- Tang 2: Rerank (cham, dien hep, chinh xac cao) ---
    print(f"[Tang 2] Dang goi LLM ({model}) de rerank + giai thich ...")
    rerank_results = rerank_with_llm(cv_data, shortlisted_jds, api_key=api_key, model=model)

    # Sap xep giam dan theo match_score, lay top K cuoi cung
    rerank_results.sort(key=lambda r: r["match_score"], reverse=True)
    return rerank_results[:final_top_k]


def main():
    parser = argparse.ArgumentParser(description="Kien truc 2 tang: embedding retrieval + LLM rerank")
    parser.add_argument("cv_file", help="File JSON CV da trich xuat")
    parser.add_argument("--jd-file", default=None, help="File JSON danh sach JD (mac dinh dung du lieu mau)")
    parser.add_argument("--retrieve-top-n", type=int, default=5, help="So JD giu lai o tang 1 (retrieval)")
    parser.add_argument("--final-top-k", type=int, default=3, help="So JD cuoi cung sau rerank")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model Gemini (mac dinh: {DEFAULT_MODEL})")
    parser.add_argument("--api-key", default=None, help="Gemini API key (mac dinh doc GEMINI_API_KEY)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Loi] Chua co API key. Set bien moi truong GEMINI_API_KEY hoac truyen --api-key.", file=sys.stderr)
        print("      Lay API key mien phi tai: https://aistudio.google.com/apikey", file=sys.stderr)
        sys.exit(1)

    with open(args.cv_file, "r", encoding="utf-8") as f:
        cv_data = json.load(f)

    if args.jd_file:
        with open(args.jd_file, "r", encoding="utf-8") as f:
            jd_list = json.load(f)
    else:
        print("[Thong bao] Khong co --jd-file, dung 5 JD mau de demo.")
        jd_list = SAMPLE_JDS

    final_results = retrieve_then_rerank(
        cv_data, jd_list, api_key=api_key,
        retrieve_top_n=args.retrieve_top_n,
        final_top_k=args.final_top_k,
        model=args.model,
    )

    print("\n=== KET QUA CUOI CUNG (sau rerank) ===")
    for i, r in enumerate(final_results, 1):
        print(f"\n{i}. [{r['job_id']}] Diem phu hop: {r['match_score']}/100")
        print(f"   Giai thich: {r['explanation']}")
        if r.get("matched_points"):
            print(f"   Diem khop: {', '.join(r['matched_points'])}")
        if r.get("missing_points"):
            print(f"   Con thieu: {', '.join(r['missing_points'])}")


if __name__ == "__main__":
    main()