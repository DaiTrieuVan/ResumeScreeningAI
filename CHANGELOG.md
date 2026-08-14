# Changelog

Tất cả thay đổi quan trọng của dự án được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [1.0.0] - 2026-08-15

### Added
- Chuyển đổi toàn bộ hệ thống sang kiến trúc Decoupled Full-stack (FastAPI Async Backend + React Vite Frontend).
- Backend RESTful API hoàn chỉnh với SQLite async (aiosqlite) và SQLAlchemy 2.0 ORM.
- Tích hợp pipeline xử lý CV: Bóc tách file PDF, chuyển đổi văn bản, tính toán Vector Embedding và chấm điểm tương đồng ngữ nghĩa.
- Dịch vụ AI Gap Advisor phân tích khoảng cách kỹ năng ứng viên và gợi ý lộ trình cải thiện chuyên sâu với Google Gemini LLM API.
- Bộ thu thập (Job Aggregator) và xếp hạng lại (Reranker) tin tuyển dụng thực tế theo mức độ phù hợp của ứng viên.
- Giao diện người dùng React 18 trực quan (Recruiter Dashboard, Gap Advisor View, Real Jobs Portal).
- Bộ test tự động (Pytest + Pytest-Asyncio) cho các API chính.
- Bổ sung file tài liệu DEPENDENCIES.md thống kê danh mục các thư viện mã nguồn mở và giấy phép đi kèm.

## [0.1.0] - 2026-07-25

### Added
- Trích xuất text từ CV định dạng PDF bằng `pdfplumber`.
- Trích xuất thông tin có cấu trúc từ CV bằng Gemini API với schema validation qua Pydantic (`cv_extract_gemini.py`).
- Engine matching CV–JD bằng semantic embedding (sentence-transformers) và KNN + cosine similarity, tự động fallback về TF-IDF (`cv_jd_matching.py`).
- Kiến trúc retrieval-then-rerank: LLM chấm điểm lại và giải thích lý do phù hợp trên tập JD đã được rút gọn (`cv_jd_rerank.py`).

### Notes
- Phiên bản Ollama local (`cv_extract_ollama.py`) đã thử nghiệm nhưng gặp lỗi tương thích CUDA trên một số máy, hiện tại dùng Gemini API làm giải pháp chính thức.