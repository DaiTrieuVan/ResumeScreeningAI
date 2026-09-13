# Implementation Plan: Recruiter Screening Workspace Upgrade

**Branch**: `codex/light-professional-ui` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-recruiter-workspace-upgrade/spec.md`

## Summary

Nâng Không gian tuyển dụng từ màn hình chấm điểm CV đơn lẻ thành một workspace ra quyết định có thể kiểm chứng: tiêu chí có phiên bản, upload hàng loạt chịu lỗi, kết luận AI có bằng chứng, danh sách hỗ trợ lọc/chọn hàng loạt, pipeline có lịch sử và chế độ so sánh finalist. Kiến trúc tiếp tục dùng React + FastAPI + SQLAlchemy hiện có, bổ sung các thực thể nghiệp vụ chuẩn hóa và API truy vấn phía server. Mỗi lát cắt được triển khai dọc từ migration, service, API, UI đến kiểm thử để luôn có một luồng dùng được.

## Technical Context

**Language/Version**: Python 3.10+; JavaScript ES2022; React 18  
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy async, aiosqlite, Gemini integration, sentence-transformers, pdfplumber; React, Vite, lucide-react  
**Storage**: SQLite và file system trong môi trường hiện tại; schema quan hệ giữ tương thích để chuyển PostgreSQL khi production  
**Testing**: pytest/pytest-asyncio cho backend; bổ sung Vitest + React Testing Library cho frontend; kiểm thử luồng bằng Playwright ở giai đoạn nghiệm thu  
**Target Platform**: Web desktop responsive; backend ASGI trên Windows/Linux  
**Project Type**: Web application gồm SPA frontend và REST/SSE backend  
**Performance Goals**: lọc/sắp xếp/phân trang dưới 1 giây với 1.000 hồ sơ; cập nhật hàng loạt 50 hồ sơ dưới 30 giây; lô tối thiểu 200 CV không bị dừng bởi lỗi cục bộ  
**Constraints**: AI chỉ đề xuất; kết quả chính thức bất biến theo phiên bản tiêu chí; không tự xóa hồ sơ trùng; dữ liệu cá nhân và thao tác xuất phải audit; giữ tương thích các API hiện tại trong giai đoạn chuyển đổi  
**Scale/Scope**: một vị trí 1.000+ hồ sơ, lô 200 CV, 2–5 ứng viên trong so sánh, một tổ chức tuyển dụng ở MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

File constitution hiện chỉ là template chưa được điền, vì vậy chưa có nguyên tắc dự án bắt buộc để đối chiếu. Plan áp dụng các guardrail mặc định sau:

- PASS — Thay đổi theo lát cắt dọc, không viết lại toàn bộ hệ thống.
- PASS — Giữ AI ở vai trò đề xuất; quyết định con người và lịch sử được lưu riêng.
- PASS — Mọi kết quả chính thức truy ngược được về input, tiêu chí và bằng chứng.
- PASS — Migration phải cộng thêm và có đường tương thích dữ liệu cũ.
- PASS — API thay đổi trạng thái phải idempotent hoặc có kiểm soát phiên bản.
- PASS — Mỗi phase có kiểm thử tự động và kịch bản nghiệm thu độc lập.

**Post-design re-check**: PASS. Data model và contract giữ nguyên các guardrail trên; chưa phát sinh ngoại lệ cần ghi vào Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/003-recruiter-workspace-upgrade/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── recruiter-workspace-api.yaml
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/                  # criteria, batches, candidates, decisions, analytics
│   ├── models/               # SQLAlchemy entities and migrations/compatibility
│   ├── repositories/         # query, pagination and transactional persistence
│   ├── schemas/              # request/response contracts
│   └── services/             # parsing, dedupe, evaluation, evidence, bulk jobs
└── tests/
    ├── contract/
    ├── integration/
    └── unit/

frontend/
├── src/
│   ├── components/
│   │   └── recruiter/        # feature-oriented reusable workspace components
│   ├── pages/
│   │   └── RecruiterDashboard.jsx
│   ├── services/             # typed request helpers and SSE client
│   └── styles/
└── tests/
    ├── components/
    └── e2e/
```

**Structure Decision**: Giữ mô hình frontend/backend hiện tại. Các component mới thuộc recruiter được gom trong `frontend/src/components/recruiter/`; backend tách endpoint theo resource thay vì tiếp tục mở rộng `screenings.py`. Logic nghiệp vụ nằm trong service/repository để API route không trực tiếp điều phối toàn bộ pipeline.

## Delivery Strategy

### Sprint 0 — Safety net và migration discipline (2–3 ngày)

- Chốt contract compatibility cho `/jobs`, `/resumes/upload`, `/screenings/*` hiện tại.
- Bổ sung Alembic hoặc cơ chế migration có version thay cho chuỗi `ALTER TABLE` thủ công.
- Tạo fixture 200 CV hỗn hợp, đo baseline thời gian upload, phân tích và truy vấn.
- Thiết lập test frontend và contract test; thêm feature flag `recruiter_workspace_v2`.

**Exit gate**: migration chạy được trên database cũ và rollback bằng bản sao dữ liệu; test hiện tại vẫn xanh.

### Sprint 1 — Nền tảng đáng tin cậy (P0, 1.5–2 tuần)

- Xây Criteria Set/Criteria có version, validation tổng trọng số 100% và trạng thái draft/published.
- Tách điểm mô phỏng khỏi Evaluation chính thức; đánh dấu stale khi criteria thay đổi.
- Chuẩn hóa kết quả tiêu chí bốn trạng thái `MET/NOT_MET/UNKNOWN/NOT_APPLICABLE`.
- Lưu evidence snippet, confidence và liên kết nguồn cho từng kết luận quan trọng.
- Thêm viewer CV gốc cạnh bảng tiêu chí; không rời khỏi ngữ cảnh ứng viên.

**Exit gate**: 100% evaluation mới có `criteria_version_id`; UI không thể nhầm điểm mô phỏng với điểm chính thức.

### Sprint 2 — Intake hàng loạt chịu lỗi (P0, 1–1.5 tuần)

- Chuyển upload thành Upload Batch + item state machine, trả batch ngay và xử lý nền.
- Giới hạn concurrency, cập nhật tiến độ ở cấp item, retry mục lỗi và tiếp tục sau reload.
- Dedupe theo file hash, contact fingerprint và content fingerprint; chỉ cảnh báo, không tự xóa.
- Phân loại lỗi: tệp hỏng, PDF ảnh cần OCR, password protected, timeout AI và lỗi hệ thống.

**Exit gate**: lô 200 CV có file lỗi vẫn hoàn tất phần còn lại; retry không tạo evaluation hoặc hồ sơ trùng ngoài ý muốn.

### Sprint 3 — Recruiter productivity (P1, 1.5 tuần)

- API candidate query phía server: search, multi-filter, sort, pagination, total/facet counts.
- Thiết kế lại bảng: cột thông tin quyết định, sticky header, column chooser, saved views.
- Selection qua nhiều trang và bulk actions có preview phạm vi, idempotency key, kết quả từng item.
- Trạng thái tải/empty/error rõ ràng và bảo toàn bộ lọc khi mở/đóng candidate drawer.

**Exit gate**: recruiter tìm được top 20 từ 500 hồ sơ dưới 3 phút; thao tác 50 hồ sơ dưới 30 giây.

### Sprint 4 — Decision workspace (P1, 1–1.5 tuần)

- Pipeline chuẩn, decision reason bắt buộc khi reject, note nội bộ và timeline append-only.
- Tách đề xuất AI, override score và quyết định con người; audit actor/time/before/after.
- Chế độ so sánh 2–5 ứng viên cùng criteria version; biểu diễn thiếu dữ liệu đúng nghĩa.
- Dashboard funnel, lỗi/trùng, thời gian xử lý trung vị và override rate.

**Exit gate**: mọi thay đổi quyết định có audit; so sánh ba finalist hoàn thành dưới 2 phút.

### Sprint 5 — Hardening và rollout (3–5 ngày)

- Kiểm thử accessibility, responsive desktop/tablet, keyboard flow và tiếng Việt dài.
- Kiểm thử tải, retry/idempotency, concurrency conflict và dữ liệu legacy.
- Bổ sung retention/anonymization, quyền xem/tải CV và audit export.
- Chạy beta theo feature flag, thu telemetry, sau đó chuyển v2 thành mặc định.

## Vertical Slices and Dependencies

1. `Criteria Versioning` → điều kiện tiên quyết cho evaluation, compare và audit.
2. `Evaluation Evidence` → phụ thuộc criteria version; là nguồn cho detail/compare.
3. `Upload Batch` → có thể triển khai song song về schema nhưng chỉ auto-evaluate khi (1) ổn định.
4. `Candidate Query + Saved View` → phụ thuộc projection của profile/evaluation.
5. `Bulk Actions + Pipeline` → phụ thuộc selection contract và audit event.
6. `Comparison + Analytics` → phụ thuộc dữ liệu versioned và decision history.

## Compatibility and Migration

- Backfill mỗi JobPosting hiện có thành Criteria Set version 1 từ `required_skills`, `preferred_skills`, kinh nghiệm, học vấn và ba trọng số.
- Backfill mỗi ScreeningResult hiện có thành Evaluation legacy; đánh dấu `evidence_status=UNAVAILABLE_LEGACY` thay vì tạo bằng chứng giả.
- Giữ endpoint cũ hoạt động trong một chu kỳ release; frontend v2 dùng `/api/recruiter/*`.
- Không đổi đường dẫn file CV khi migration; tạo checksum theo tác vụ nền và giới hạn I/O.
- Thực hiện dual-read ngắn hạn cho status hiện tại; mọi write mới đi qua Decision Event và cập nhật projection trong cùng transaction.

## Quality Gates

- Unit: validation trọng số, state machine, dedupe scoring, criteria evaluation, stale detection.
- Contract: request/response và error codes trong OpenAPI.
- Integration: upload mixed batch, retry, evaluate, filter, bulk transition, compare, audit.
- E2E: ba journey trong `quickstart.md` trên viewport desktop và tablet.
- Load: 1.000 candidates query; 200-file batch; 50-item bulk action.
- Security/privacy: path traversal upload, file type/size, access to original CV, export audit, anonymization.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| SQLite lock contention khi nhiều worker ghi | Tiến độ/lưu kết quả lỗi ngắt quãng | Giới hạn writer concurrency, transaction ngắn; giữ abstraction để chuyển PostgreSQL |
| AI tạo kết luận không có căn cứ | Mất niềm tin và quyết định sai | Evidence bắt buộc, UNKNOWN khi thiếu nguồn, human decision tách riêng |
| Criteria đổi giữa lúc batch chạy | Các ứng viên không còn so sánh cùng chuẩn | Batch pin một criteria version; bản mới chỉ áp dụng khi re-run |
| Dedupe false positive | Bỏ sót ứng viên | Chỉ cảnh báo với lý do/độ tin cậy; recruiter quyết định |
| Scope UI quá lớn | Chậm có giá trị sử dụng | Feature flag và ship theo vertical slice/Sprint exit gate |

## Complexity Tracking

Không có vi phạm constitution cần biện minh. Việc thêm các bảng version/audit là cần thiết để đáp ứng truy vết; không đưa message broker hoặc search engine mới vào MVP.
