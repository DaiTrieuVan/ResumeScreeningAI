# Direct Dependencies and Licenses

Tài liệu này ghi nhận các dependency trực tiếp của Resume Screening AI. Phiên
bản thực tế được giải quyết bởi `backend/requirements.txt`, bộ mở rộng
`backend/requirements-optional.txt` và `frontend/package-lock.json`. Dependency
được cài qua `pip`/`npm`; repository
không sao chép hoặc chỉnh sửa mã nguồn của các gói này.

## Backend runtime

| Package | Constraint | License | Purpose |
|---|---:|---|---|
| FastAPI | `>=0.115.0` | MIT | REST API framework |
| Uvicorn | `>=0.30.0` | BSD-3-Clause | ASGI server |
| Pydantic | `>=2.8.0` | MIT | Schema validation |
| pydantic-settings | `>=2.4.0` | MIT | Environment configuration |
| SQLAlchemy | `>=2.0.30` | MIT | Async ORM and migrations |
| aiosqlite | `>=0.20.0` | MIT | Async SQLite driver |
| aiofiles | `>=23.2.0` | Apache-2.0 | Async CV file storage |
| pdfplumber | `>=0.11.0` | MIT | PDF text extraction |
| google-genai | `>=0.1.1` | Apache-2.0 | Optional Gemini API SDK |
| NumPy | `>=1.26.0` | BSD-3-Clause | Vector calculations |
| python-multipart | `>=0.0.9` | Apache-2.0 | Multipart uploads |
| HTTPX | `>=0.27.0` | BSD-3-Clause | Async HTTP client and API tests |

`sentence-transformers>=3.0.0` (Apache-2.0) và
`crawl4ai>=0.5.0.post8` (Apache-2.0) nằm trong
`requirements-optional.txt`; bản cài tối thiểu không tải model/browser runtime.

## Backend test dependencies

| Package | Constraint | License | Purpose |
|---|---:|---|---|
| pytest | `>=8.2.0` | MIT | Test runner |
| pytest-asyncio | `>=0.23.0` | Apache-2.0 | Async test support |

## Frontend runtime

| Package | Constraint | License | Purpose |
|---|---:|---|---|
| React | `^18.3.1` | MIT | User interface |
| react-dom | `^18.3.1` | MIT | Browser rendering |
| lucide-react | `^0.420.0` | ISC | Accessible SVG icons |

## Frontend build and test dependencies

| Package | Constraint | License | Purpose |
|---|---:|---|---|
| Vite | `^8.3.0` | MIT | Development server and build |
| @vitejs/plugin-react | `^6.1.1` | MIT | JSX/Fast Refresh integration |
| Vitest | `^5.0.0` | MIT | Component test runner |
| jsdom | `^25.0.1` | MIT | Browser-like test environment |
| @testing-library/react | `^16.1.0` | MIT | Component interaction tests |
| @testing-library/jest-dom | `^6.6.3` | MIT | DOM assertions |
| @types/react | `^18.3.3` | MIT | React type definitions |
| @types/react-dom | `^18.3.0` | MIT | React DOM type definitions |
| @playwright/test | `^1.63.0` | Apache-2.0 | End-to-end browser tests |

## CI actions

| Action | Version | License | Purpose |
|---|---:|---|---|
| actions/checkout | `v4` | MIT | Checkout repository in CI |
| actions/setup-python | `v5` | MIT | Provision and cache Python |
| actions/setup-node | `v4` | MIT | Provision and cache Node.js |

## External services and downloaded models

- **Google Gemini** is an optional hosted service. Its SDK is Apache-2.0, but
  the hosted model/service is governed by Google's service terms and is not
  distributed in this repository.
- **Hugging Face sentence-transformer weights** may be downloaded on first use.
  Model-card license and intended-use information must be reviewed for the
  selected value before redistributing model weights. This repository does not
  bundle those weights.
- **TopCV and ITViec** remain owners of their content and trademarks. The live
  crawler stores links and limited job metadata for demonstration; deployers
  must comply with source terms, robots policy and applicable law.

## Bundling policy

- Không commit `venv/`, `node_modules/`, browser binaries hoặc model weights.
- Không sửa mã nguồn dependency trong repository.
- Bản phát hành ưu tiên source `.tar.gz`; người dùng cài dependency từ registry.
- `package-lock.json` được commit để giữ cây frontend có thể tái lập.
- Trước mỗi release, chạy `pip-licenses`/SBOM và `npm audit`; mọi dependency mới
  phải được thêm vào tài liệu này.

## Compatibility statement

Các dependency trực tiếp nêu trên sử dụng giấy phép permissive được phép dùng
cùng dự án MIT. Bản quyền và điều khoản của từng dependency không bị thay thế
bởi giấy phép MIT của dự án. Nếu metadata upstream thay đổi, release owner phải
đánh giá lại trước khi phát hành.
