# Resume Screening AI

Nền tảng mã nguồn mở hỗ trợ nhà tuyển dụng sàng lọc CV có bằng chứng và giúp
người tìm việc khám phá công việc, nhận diện khoảng trống kỹ năng bằng AI.

[![License: MIT](https://img.shields.io/badge/License-MIT-0f9f75.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/DaiTrieuVan/ResumeScreeningAI)](https://github.com/DaiTrieuVan/ResumeScreeningAI/releases)

> AI là công cụ hỗ trợ ra quyết định. Hệ thống không nên được dùng để tự động
> từ chối ứng viên hoặc thay thế đánh giá của con người.

## Bài toán và giá trị

Một đợt tuyển dụng có thể nhận hàng trăm CV với định dạng và cách diễn đạt khác
nhau. Việc đọc thủ công mất thời gian, còn một điểm số AI không có bằng chứng
dễ tạo niềm tin sai. Resume Screening AI kết hợp quy trình nghiệp vụ, semantic
matching và giải thích theo tiêu chí để người tuyển dụng biết **vì sao** một hồ
sơ phù hợp, dữ liệu nào còn thiếu và quyết định nào do con người thực hiện.

## Bốn phân hệ chính

1. **Recruiter Workspace** - quản lý JD và phiên bản tiêu chí, upload CV theo
   batch, phát hiện trùng lặp, theo dõi tiến độ, lọc 500+ ứng viên và thao tác hàng loạt.
2. **Candidate Evidence Review** - xem CV cạnh kết quả từng tiêu chí
   `MET / NOT_MET / UNKNOWN / NOT_APPLICABLE`, trích dẫn nguồn và độ tin cậy.
3. **Real Jobs Portal** - tổng hợp tin tuyển dụng, nhận diện lĩnh vực CV và xếp
   hạng công việc theo mức phù hợp; có dữ liệu fallback cho demo.
4. **Career Gap Advisor** - so sánh CV với JD mục tiêu và đề xuất lộ trình cải thiện.

Recruiter Workspace còn hỗ trợ so sánh finalist trên cùng phiên bản tiêu chí,
timeline quyết định có audit, optimistic locking, saved view, analytics funnel
và luồng ẩn danh dữ liệu ứng viên.

## Điểm khác biệt kỹ thuật

- Điểm chính thức luôn gắn với một phiên bản tiêu chí đã publish.
- Kết luận quan trọng đi kèm evidence; thiếu dữ liệu được biểu diễn là
  `UNKNOWN`, không bị coi nhầm là không đạt.
- AI recommendation và quyết định của recruiter được lưu riêng để truy vết.
- Batch upload chịu lỗi từng file; retry không làm mất kết quả đã thành công.
- Gemini là tùy chọn. Khi không có API key, hệ thống dùng pipeline local/fallback.
- CV gốc và dữ liệu cá nhân có kiểm soát truy cập, audit và luồng ẩn danh.

## Kiến trúc

```text
React + Vite
    │  REST / SSE under /api
    ▼
FastAPI ── services ── SQLAlchemy async ── SQLite
    │          │
    │          ├── PDF extraction and structured metadata
    │          ├── Sentence Transformer / keyword fallback
    │          ├── Gemini reasoning / deterministic fallback
    │          └── Job crawler / curated demo feed
    ▼
Local CV storage with access audit and anonymization
```

Chi tiết tại [Kiến trúc hệ thống](docs/ARCHITECTURE.md) và
[Thiết kế AI](docs/AI_SYSTEM.md).

## Khởi chạy nhanh từ mã nguồn

Yêu cầu: Python 3.10+, Node.js 18+ và Git.

### Backend

```powershell
git clone https://github.com/DaiTrieuVan/ResumeScreeningAI.git
cd ResumeScreeningAI\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Trên Linux/macOS, thay lệnh activate bằng `source venv/bin/activate` và sao
chép cấu hình bằng `cp .env.example .env`.

### Frontend

Mở terminal thứ hai:

```powershell
cd ResumeScreeningAI\frontend
npm install
npm run dev
```

- Web: <http://localhost:5173>
- API docs: <http://127.0.0.1:8000/api/docs>
- Health check: <http://127.0.0.1:8000/health>

`GEMINI_API_KEY` không bắt buộc. Để demo hoàn toàn local, giữ khóa trống và đặt
`DISABLE_EMBEDDING_MODEL=true`. Xem đầy đủ tại
[Build và triển khai](docs/BUILD_AND_DEPLOYMENT.md).

## Kiểm thử

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm test -- --run
npm run test:e2e
npm run build
```

Bộ kiểm thử hiện bao gồm unit, contract, integration, component và Playwright
E2E cho keyboard, responsive, drawer scrolling và candidate comparison.

## Cấu trúc repository

```text
backend/app/        FastAPI API, domain models, repositories và services
backend/tests/      Unit, contract và integration tests
frontend/src/       React components, pages, API clients và styles
frontend/tests/     Playwright acceptance journeys
specs/              Feature specifications, plans, contracts và task history
docs/               Architecture, AI, build, testing, privacy và demo guide
.github/             Issue và pull request templates
```

## Tài liệu

- [Build và triển khai](docs/BUILD_AND_DEPLOYMENT.md)
- [Kiến trúc hệ thống](docs/ARCHITECTURE.md)
- [Thiết kế và đánh giá AI](docs/AI_SYSTEM.md)
- [Kiểm thử](docs/TESTING.md)
- [Quyền riêng tư và Responsible AI](docs/PRIVACY_AND_RESPONSIBLE_AI.md)
- [Kịch bản demo](docs/DEMO_GUIDE.md)
- [Kịch bản thuyết trình 6 phút 30 giây](docs/SHOWCASE_SCRIPT.md)
- [Checklist cuộc thi](docs/COMPETITION_CHECKLIST.md)
- [Thư viện và giấy phép](DEPENDENCIES.md)
- [Hướng dẫn đóng góp](CONTRIBUTING.md)
- [Chính sách bảo mật](SECURITY.md)
- [Lịch sử thay đổi](CHANGELOG.md)

## Giới hạn hiện tại

- Trích xuất CV ảnh phụ thuộc khả năng đọc PDF và chưa có OCR chuyên dụng.
- Semantic score phản ánh độ tương đồng văn bản, không chứng minh năng lực thực tế.
- Live crawler phụ thuộc cấu trúc và điều khoản của website nguồn; demo feed được
  dùng khi nguồn ngoài không khả dụng.
- Header vai trò hiện phục vụ prototype; triển khai doanh nghiệp cần tích hợp
  hệ thống xác thực và phân quyền phía server.
- Mọi quyết định tuyển dụng cuối cùng phải do người có trách nhiệm xem xét.

## Đóng góp và quản lý lỗi

GitHub Issues là bug tracker chính: <https://github.com/DaiTrieuVan/ResumeScreeningAI/issues>.
Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) và không đăng dữ liệu ứng viên thật.

## Giấy phép

Copyright (c) 2026 226789SBTC - Trieu Van Dai.

Dự án được phát hành theo [MIT License](LICENSE), giấy phép được OSI phê chuẩn.
Các dependency giữ nguyên giấy phép của chủ sở hữu tương ứng; xem
[DEPENDENCIES.md](DEPENDENCIES.md) và [NOTICE](NOTICE).
