# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

from app.services.gap_advisor_service import fallback_gap_analysis, sanitize_gap_output


def test_fallback_keeps_multi_word_technology_names_together():
    result = fallback_gap_analysis(
        "Java developer with Spring Boot and REST API experience",
        "Built Java services using Spring Boot and REST API",
    )

    assert "Spring Boot" in result["matched_skills"]
    assert "RESTful API" in result["matched_skills"]
    assert "Spring" not in result["matched_skills"]
    assert "Boot" not in result["matched_skills"]
    assert "Spring, Boot" not in result["category_details"]["ky_nang"]


def test_sanitizer_repairs_split_skills_and_technical_text():
    result = sanitize_gap_output(
        {
            "matched_skills": ["Java", "Spring", "Boot", "Mysql"],
            "missing_skills": ["Rest", "Api", "Postgresql", "Git", "Git"],
            "category_details": {
                "ky_nang": "Đã thể hiện tốt Java, Spring, Boot và Mysql."
            },
            "strengths": ["Có nền tảng kỹ thuật."],
            "weaknesses": ["Cần bổ sung kinh nghiệm."],
            "suggested_action_items": ["Hoàn thiện CV."],
        }
    )

    assert result["matched_skills"] == ["Java", "Spring Boot", "MySQL"]
    assert result["missing_skills"] == ["RESTful API", "PostgreSQL", "Git"]
    assert result["category_details"]["ky_nang"] == "Đã thể hiện tốt Java, Spring Boot và MySQL."
