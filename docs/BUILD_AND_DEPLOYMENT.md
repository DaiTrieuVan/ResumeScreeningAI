# Build and Deployment Guide

## 1. Prerequisites

- Git 2.40+
- Python 3.10+
- Node.js 18+ và npm
- Khoảng 4 GB trống nếu tải sentence-transformer/browser crawler
- Gemini API key chỉ khi muốn dùng reasoning từ dịch vụ ngoài

Mọi công cụ bắt buộc để build đều là mã nguồn mở. Không cần IDE hoặc compiler
nguồn đóng.

## 2. Clone và kiểm tra phiên bản

```powershell
git clone https://github.com/DaiTrieuVan/ResumeScreeningAI.git
cd ResumeScreeningAI
git status
git describe --tags --always
```

Với bản dự thi, checkout đúng tag được công bố thay vì một branch đang thay đổi.

## 3. Backend trên Windows

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`requirements.txt` là bộ cài tối thiểu, hỗ trợ fallback offline. Chỉ cài
`requirements-optional.txt` khi cần sentence-transformer và live crawler.

## 4. Backend trên Linux/macOS

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ứng dụng tạo SQLite database và `storage/resumes` khi khởi động. Chạy từ thư mục
`backend` để đường dẫn tương đối trong `.env` có ý nghĩa thống nhất.

## 5. Frontend development

```powershell
cd frontend
npm install
npm run dev
```

Vite proxy chuyển `/api` sang `http://127.0.0.1:8000`. Browser mở
<http://localhost:5173>.

## 6. Production build

```powershell
cd frontend
npm ci
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Thư mục `frontend/dist` là output có thể triển khai. Web server production phải:

1. phục vụ SPA/static files từ `dist`;
2. fallback route frontend về `index.html`;
3. reverse proxy `/api/*` tới FastAPI;
4. bật HTTPS và giới hạn upload phù hợp.

Không commit `dist`; release được build lại từ source và lockfile.

## 7. Configuration reference

| Variable | Required | Default/example | Purpose |
|---|---|---|---|
| `PROJECT_NAME` | No | `Resume Screening AI` | API metadata |
| `API_V1_STR` | No | `/api` | API prefix |
| `DATABASE_URL` | No | SQLite local | Database connection |
| `STORAGE_DIR` | No | `./storage/resumes` | CV file root |
| `GEMINI_API_KEY` | No | empty | Optional Gemini access |
| `DEFAULT_LLM_MODEL` | No | configured model name | Gemini model |
| `DEFAULT_EMBEDDING_MODEL` | No | multilingual MiniLM | Embedding model |
| `DISABLE_EMBEDDING_MODEL` | No | `false` | Force keyword fallback |
| `OFFLINE_MODE` | No | `false` | Chặn dịch vụ ngoài và dùng dữ liệu/fallback cục bộ |
| `OFFLINE_ENGINE` | No | `deterministic-keyword-v1` | Nhãn engine khi chạy offline |
| `RECRUITER_WORKSPACE_V2_ENABLED` | No | `true` | Rollout signal |

Không đưa `.env` vào source control. Sau khi thay key, restart backend.

## 8. Optional live crawler

Live crawling cần browser runtime và có thể phụ thuộc điều khoản nguồn:

```powershell
playwright install chromium
```

Nếu browser/network không sẵn sàng, ứng dụng dùng curated demo feed. Không nên
cài browser hoặc tải model lần đầu ngay trong phần trình diễn.

## 9. Database migration, backup và rollback

Trước rollout:

```powershell
Copy-Item backend\resume_screening.db backend\resume_screening.backup.db
Copy-Item backend\storage backend\storage-backup -Recurse
```

Migration chạy khi FastAPI startup và được thiết kế idempotent. Sau migration,
chạy health/API smoke test. Rollback application không tự xóa bảng v2; giữ dữ
liệu để tránh mất lịch sử. Không sử dụng backup chứa CV thật cho demo công khai.

## 10. Clean-room verification

Trên một thư mục/máy mới:

1. Clone đúng release tag hoặc tải source archive chính thức.
2. Chạy `scripts\verify_clean_room.ps1 -SourceMode Archive` từ repository gốc.
3. Script tạo đường dẫn tạm mới, cài lại dependency và chạy safety, compliance,
   backend, benchmark, frontend, build cùng E2E.
4. Đối chiếu JSON kết quả với `release/verification-record.md` và checksum asset.
5. Tạo JD mẫu, upload CV tổng hợp, chạy screening và mở evidence trên máy demo.
6. Ngắt network và xác nhận badge `Offline` cùng fallback vẫn hoàn tất hành trình.

## 11. Troubleshooting

- **Không kết nối API**: xác nhận backend port 8000 và `/api` reverse proxy.
- **Embedding tải lâu**: đặt `DISABLE_EMBEDDING_MODEL=true` cho demo local.
- **Gemini lỗi**: để key trống, kiểm tra fallback và không log key.
- **PDF không có text**: dùng PDF số hoặc đưa item sang manual review.
- **Crawler lỗi**: dùng dữ liệu fallback; không retry liên tục website nguồn.
- **SQLite locked**: dừng process cũ; production concurrent nên dùng PostgreSQL.
