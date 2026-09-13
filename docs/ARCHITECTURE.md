# System Architecture

## 1. Mục tiêu kiến trúc

Resume Screening AI tách giao diện, API, nghiệp vụ, persistence và tích hợp AI
để mỗi phần có thể kiểm thử độc lập. Các nguyên tắc chính:

- AI không ghi đè quyết định của con người.
- Điểm số phải tái hiện được từ criteria version và input fingerprint.
- Thiếu bằng chứng là `UNKNOWN`, không phải `NOT_MET`.
- Lỗi một CV không làm hỏng toàn batch.
- Không log raw CV hoặc PII không cần thiết.
- API legacy được giữ trong giai đoạn rollout để bảo đảm tương thích.

## 2. Sơ đồ container

```text
┌──────────────────────── Browser ────────────────────────┐
│ React 18 + Vite                                        │
│ Recruiter | Candidate Detail | Real Jobs | Gap Advisor │
└───────────────────────┬─────────────────────────────────┘
                        │ /api REST + SSE
┌───────────────────────▼─────────────────────────────────┐
│ FastAPI                                                  │
│ routers -> schemas -> services -> repositories           │
├─────────────────┬───────────────────┬────────────────────┤
│ Screening       │ AI adapters       │ External jobs      │
│ criteria/evidence│ Gemini/embedding │ Playwright/Crawl4AI│
└────────┬────────┴──────────┬────────┴──────────┬─────────┘
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│ SQLite          │ │ Local CV store │ │ External sites  │
│ SQLAlchemy async│ │ access audited │ │ or demo feed    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 3. Backend layers

- `app/api`: HTTP contract, validation, status codes và dependency injection.
- `app/schemas`: Pydantic request/response contracts.
- `app/services`: orchestration và domain policies.
- `app/repositories`: reusable query/analytics projections.
- `app/models`: SQLAlchemy entities và domain enums.
- `app/core`: configuration, storage, database, migrations và error handling.

API documentation được sinh tự động tại `/api/docs`. Error response nghiệp vụ
dùng mã ổn định trong `detail.code`; concurrent write dùng `If-Match` và trả 409.

## 4. Screening data flow

```text
Job/JD
  -> CriteriaSet draft
  -> validate weights and publish immutable version
CV batch
  -> validate/dedupe/parse
  -> CandidateApplication
  -> OFFICIAL or SIMULATION evaluation
  -> CriterionResult + EvidenceSnippet
  -> mandatory gate + component scores + overall score
  -> recruiter review/compare/decision
  -> append-only DecisionEvent + AuditEvent
```

`ScreeningResult` giữ compatibility cho API cũ. Mô hình v2 sử dụng
`CandidateApplication`, `ScreeningEvaluation`, `CriterionResult` và
`EvidenceSnippet` để truy vết chi tiết.

## 5. Upload batch state machine

Mỗi upload tạo `UploadBatch` và nhiều `UploadItem`. Item đi qua validation,
duplicate review, parsing và completion độc lập. Batch tổng hợp count từ item;
retry chỉ áp dụng item thất bại và tăng attempt counter. Fingerprint nội dung và
contact giúp phát hiện exact/contact duplicate mà không tự động xóa hồ sơ.

## 6. Decision consistency

Mỗi `CandidateApplication` có `version`. Client gửi version dự kiến qua
`If-Match`; server từ chối thay đổi cũ bằng 409. Mọi chuyển stage/decision tạo
event append-only chứa actor, before/after và reason. AI recommendation được giữ
riêng với human decision để đo override và phục vụ audit.

## 7. Persistence và migration

SQLite phù hợp demo/local. Migration runner là additive và idempotent: thêm cột,
bảng và index mà không xóa dữ liệu legacy. Trước rollout phải sao lưu file DB và
`backend/storage/resumes`. Production nhiều người dùng nên chuyển sang PostgreSQL,
object storage và migration framework chuyên dụng.

## 8. Security boundaries

- Upload kiểm tra đường dẫn và chỉ phục vụ file nằm trong storage root.
- Dữ liệu cá nhân yêu cầu role, tạo access audit và hỗ trợ anonymization.
- Prototype nhận actor/role qua header; đây không phải cơ chế xác thực production.
- Production cần identity provider, server-side role mapping, TLS, CSRF policy,
  rate limiting, malware scanning và encrypted storage.

## 9. Quality attributes

- **Reliability**: per-item failure, retry, idempotency key và optimistic locking.
- **Explainability**: criteria version, evidence, confidence, model metadata.
- **Performance**: query indexes, server-side pagination, cached embeddings.
- **Accessibility**: semantic dialog/regions, keyboard journeys, responsive CTA.
- **Testability**: external AI có fallback; E2E mock API deterministically.
