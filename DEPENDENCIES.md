# Thư viện & Gói mã nguồn mở phụ thuộc (Dependencies & Licenses)

Dự án **Resume Screening AI Project** cam kết tuân thủ tiêu chuẩn mã nguồn mở (Proof of Freedom - PoF). Tất cả các thư viện và công cụ được sử dụng đều là mã nguồn mở với giấy phép OSI-approved.

---

## 1. Backend (Python Dependencies)

| Thư viện / Gói | Phiên bản | Giấy phép (License) | Mục đích sử dụng trong dự án |
| :--- | :--- | :--- | :--- |
| **FastAPI** | >= 0.115.0 | MIT License | Web Framework chính xây dựng bất đồng bộ RESTful APIs |
| **Uvicorn** | >= 0.30.0 | BSD 3-Clause | ASGI web server cho FastAPI |
| **Pydantic** | >= 2.8.0 | MIT License | Data validation và định nghĩa DTO schemas |
| **Pydantic-Settings** | >= 2.4.0 | MIT License | Quản lý biến cấu hình môi trường (.env) |
| **SQLAlchemy** | >= 2.0.30 | MIT License | ORM tương tác bất đồng bộ với cơ sở dữ liệu |
| **aiosqlite** | >= 0.20.0 | MIT License | Driver bất đồng bộ kết nối SQLite database |
| **pdfplumber** | >= 0.11.0 | MIT License | Bóc tách và trích xuất dữ liệu văn bản từ file CV (PDF) |
| **google-genai** | >= 0.1.1 | Apache-2.0 | SDK tích hợp Google Gemini API cho tính năng AI Gap Advisor |
| **sentence-transformers** | >= 3.0.0 | Apache-2.0 | Tạo Vector Embeddings biểu diễn ngữ nghĩa CV & Job Description |
| **numpy** | >= 1.26.0 | BSD 3-Clause | Tính toán đại số tuyến tính & độ tương đồng Cosine (Cosine Similarity) |
| **python-multipart** | >= 0.0.9 | Apache-2.0 | Xử lý upload file CV định dạng multipart/form-data |
| **httpx** | >= 0.27.0 | BSD 3-Clause | Async HTTP client phục vụ thu thập dữ liệu công việc |
| **pytest** | >= 8.2.0 | MIT License | Khung kiểm thử tự động (Unit / Integration Tests) |
| **pytest-asyncio** | >= 0.23.0 | Apache-2.0 | Hỗ trợ chạy các bài test bất đồng bộ (async tests) |

---

## 2. Frontend (JavaScript / React Dependencies)

| Thư viện / Gói | Phiên bản | Giấy phép (License) | Mục đích sử dụng trong dự án |
| :--- | :--- | :--- | :--- |
| **React** | ^18.3.1 | MIT License | Thư viện UI xây dựng Single Page Application |
| **React-DOM** | ^18.3.1 | MIT License | Render Virtual DOM cho môi trường trình duyệt |
| **Vite** | ^5.4.0 | MIT License | Công cụ đóng gói và chạy Dev Server giao diện |
| **Lucide-React** | ^0.420.0 | ISC License | Bộ biểu tượng icon giao diện người dùng |
| **@vitejs/plugin-react** | ^4.3.1 | MIT License | Plugin hỗ trợ Fast Refresh và JSX cho React trong Vite |

---

## 3. Xác nhận tuân thủ Giấy phép (Compliance Statement)

- Tất cả các gói và thư viện đính kèm được sử dụng nguyên bản thông qua trình quản lý gói tiêu chuẩn (`pip` cho Python và `npm` cho Node.js).
- Mã nguồn của các gói đính kèm không bị sửa đổi thủ công.
- Giấy phép của toàn bộ các thư viện phụ thuộc đều tương thích hoàn toàn với giấy phép mở **MIT License** của dự án.
