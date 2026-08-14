#Resume Screening AI Project

Hệ thống tự động rà soát, đánh giá và phân tích khoảng cách kỹ năng (Gap Analysis) của ứng viên dựa trên CV (PDF) và Mô tả công việc (Job Description) bằng AI.

---

##Tính năng chính

1. **Bóc tách dữ liệu CV (PDF Parsing):** Trích xuất tự động thông tin từ file CV định dạng PDF.
2. **So khớp ứng viên bằng Vector Embedding:** Sử dụng `Sentence Transformers` (mô hình `all-MiniLM-L6-v2`) để tính toán độ tương đồng ngữ nghĩa giữa CV và Mô tả công việc.
3. **AI Gap Advisor (Gemini LLM):** Phân tích các điểm thiếu hụt kỹ năng (Skill Gaps) của ứng viên và đưa ra gợi ý lộ trình cải thiện chuyên sâu.
4. **Aggregator & Reranker Công việc Thực tế:** Tìm kiếm, thu thập và xếp hạng công việc thực tế theo tiêu chí phù hợp với ứng viên.
5. **Dashboard Nhà tuyển dụng:** Giao diện quản lý tin tuyển dụng, upload danh sách CV, xem báo cáo điểm số và xuất báo cáo kết quả.

---

##Công nghệ sử dụng

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, Uvicorn
- **AI & NLP:** Google Gemini API (`google-genai`), Sentence-Transformers, NumPy, pdfplumber
- **Frontend:** React 18, Vite, Lucide Icons, Vanilla CSS
- **Database:** SQLite (`aiosqlite`)

---

##Hướng dẫn cài đặt & Khởi chạy

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Trên Windows
pip install -r requirements.txt

# (Tùy chọn) Cấu hình .env
# GEMINI_API_KEY=your_key_here

uvicorn app.main:app --reload --port 8000
```
- API Documentation: [http://127.0.0.1:8000/api/docs](http://127.0.0.1:8000/api/docs)

### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
- Giao diện người dùng: [http://localhost:5173](http://localhost:5173)

---

##Cấu trúc dự án

```
Resume Screening AI Project/
├── backend/
│   ├── app/
│   │   ├── api/          # REST API Controllers
│   │   ├── core/         # Config, Database & Exception handling
│   │   ├── models/       # SQLAlchemy Database Models
│   │   ├── schemas/      # Pydantic DTOs
│   │   ├── services/     # AI Services, Embedding, PDF Parser, Gap Advisor
│   │   └── main.py       # FastAPI Application Entrypoint
│   ├── tests/            # Test Suites (Pytest)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # UI Components
│   │   ├── pages/        # Views/Pages (Dashboard, GapAdvisor, RealJobs)
│   │   ├── services/     # API Client Service
│   │   └── styles/       # CSS Styles
│   ├── package.json
│   └── vite.config.js
└── specs/                # Product Specification & Feature Planning Documents
```
