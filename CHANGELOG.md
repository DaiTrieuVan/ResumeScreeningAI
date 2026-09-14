# Changelog

Tất cả thay đổi quan trọng của dự án được ghi lại trong file này.

Định dạng dựa trên [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/),
và dự án tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

### Added
- Recruiter Workspace v2 với criteria versioning, mandatory/preferred/bonus requirements và mô phỏng trọng số trước khi publish.
- Batch upload bền vững, trạng thái từng file, phát hiện trùng lặp và retry có kiểm soát.
- Candidate evidence review hiển thị kết quả từng tiêu chí, confidence và trích dẫn từ CV.
- Candidate triage với filter/sort/pagination, saved views, cross-page selection và bulk actions.
- Decision pipeline có optimistic locking, reason bắt buộc, timeline và audit trail.
- So sánh 2-5 finalist trên cùng criteria version và biểu diễn `UNKNOWN` tách biệt.
- Recruiter analytics cho funnel, chất lượng upload, thời gian xử lý và tỷ lệ override AI.
- Access audit và anonymization xóa CV gốc, PII cùng nội dung dẫn xuất nhạy cảm.
- Playwright acceptance journeys cho keyboard, responsive, scrolling và comparison.
- Bộ tài liệu mã nguồn mở, AI, quyền riêng tư, build/deploy và showcase cuộc thi.
- Blind Review phía server cho list, detail, comparison, evidence và CSV; reveal
  CV gốc là thao tác có chủ đích và được audit.
- Chế độ offline xác định, runtime status badge, benchmark 30 CV tổng hợp / 3 JD
  và clean-room verification có machine-readable record.

### Changed
- Refactor giao diện theo phong cách sáng, chuyên nghiệp và responsive.
- Trang khám phá việc làm sử dụng hero banner toàn chiều rộng.
- Sentence Transformer được lazy-load để ứng dụng và test khởi động ổn định.
- Tách sentence-transformer/Crawl4AI sang bộ dependency tùy chọn; bản cài tối
  thiểu vẫn chạy đầy đủ fallback offline.
- Nâng Vite/Vitest/plugin React để full npm audit đạt 0 vulnerability.

### Fixed
- Candidate detail drawer có vùng cuộn độc lập, không còn bị kẹt ở viewport thấp.
- Test discovery không còn tải model embedding nặng.

### Security
- Kiểm tra vai trò khi xem/tải/xuất dữ liệu ứng viên.
- Audit các lần xem chi tiết, mở CV gốc, xuất CSV và ẩn danh.
- Loại bỏ dữ liệu evidence và ghi chú có thể chứa PII khi ẩn danh.

### Measured release-candidate evidence
- Backend: 54 tests; frontend: 15 component tests; Playwright: 7 journeys.
- AI benchmark: mandatory recall, evidence precision, UNKNOWN accuracy, ranking
  agreement và batch completion đều đạt `1.0000` trên dataset tổng hợp versioned.
- Clean-room committed source archive hoàn tất trong 1.72 phút; final `main` archive
  vẫn phải chạy lại sau khi merge.

### Known limitations
- Benchmark tổng hợp không đại diện độ chính xác tuyển dụng ngoài thực tế.
- SQLite/local storage và role headers chỉ phù hợp demo; production cần identity
  provider, PostgreSQL/object storage, encryption và retention policy.
- OCR cho scanned PDF và độ ổn định dịch vụ/crawler ngoài vẫn là giới hạn; bản
  dự thi dùng fallback offline và luôn giữ quyết định cuối cho con người.

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
