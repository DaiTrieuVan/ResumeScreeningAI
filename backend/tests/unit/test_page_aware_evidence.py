# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from app.services.evidence_service import find_text_evidence
from app.services.pdf_parser import build_page_records


def test_page_records_preserve_global_offsets_and_one_based_pages():
    full_text, pages = build_page_records(["Python on first page", "FastAPI on second page"])
    evidence = find_text_evidence(full_text, ["FastAPI"], pages=pages)
    assert evidence["page_number"] == 2
    assert evidence["source_method"] == "NATIVE"
    assert full_text[evidence["start_offset"]:evidence["end_offset"]] == "FastAPI"


def test_duplicate_excerpt_maps_to_page_containing_selected_global_offset():
    full_text, pages = build_page_records(["SQL", "SQL and Python"])
    evidence = find_text_evidence(full_text, ["Python"], pages=pages)
    assert evidence["page_number"] == 2


def test_legacy_text_never_invents_page_number():
    evidence = find_text_evidence("Python developer", ["Python"])
    assert evidence["page_number"] is None
    assert evidence["source_method"] == "LEGACY_UNKNOWN"

