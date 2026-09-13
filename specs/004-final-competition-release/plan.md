# Implementation Plan: Final Competition Release

**Branch**: `docs/competition-documentation` | **Date**: 2026-09-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-final-competition-release/spec.md`

## Summary

Đóng Resume Screening AI thành bản dự thi có thể tái tạo và bảo vệ trước phản biện kỹ thuật. Kế hoạch ưu tiên đo baseline AI trước, sau đó hoàn thiện evidence theo trang/correction, batch recovery/idempotency, manual recovery cho PDF scan và blind review. Cuối cùng chạy full gate trên máy sạch, merge vào `main`, tạo release có checksum/SBOM/benchmark và diễn tập showcase offline. Không mở rộng sang chatbot, email, scheduling, ATS integration hoặc hạ tầng multi-node.

## Technical Context

**Language/Version**: Python 3.10+; JavaScript ES2022/JSX trên Node.js 18+

**Primary Dependencies**: FastAPI, SQLAlchemy async, Pydantic, pdfplumber, NumPy, optional sentence-transformers/Google GenAI; React 18, Vite, lucide-react

**Storage**: SQLite + local CV storage cho bản thi; JSON/Markdown artifacts cho dataset, benchmark và release evidence

**Testing**: pytest/pytest-asyncio; Vitest + Testing Library; Playwright E2E; compliance, secret/PII, dependency/license và clean-room scripts

**Target Platform**: Windows 10/11 demo laptop và Linux GitHub Actions; evergreen Chromium/Edge; chạy offline là bắt buộc

**Project Type**: Full-stack web application với REST/SSE API và evaluation/release tooling

**Performance Goals**: Batch 200 CV không mất kết quả khi có lỗi/restart; truy vấn 1.000 ứng viên phản hồi trong 1 giây ở điều kiện demo; evidence/correction journey dưới 90 giây; clean-room setup dưới 30 phút

**Constraints**: Không dùng CV thật; không auto-reject; không bắt buộc API key/network; không bundle dependency source/model; source release ưu tiên `.tar.gz`; hoàn tất trước hạn nộp 30/09/2026

**Scale/Scope**: Một máy/single-node competition deployment; 3 JD và tối thiểu 30 CV benchmark; tối đa 200 CV/lô; 5 user journeys final; giữ nguyên bốn phân hệ hiện có

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Tệp constitution hiện là template chưa ratify nên không có rule có hiệu lực để đánh giá. Kế hoạch áp dụng quality gate đã được dự án công bố thay thế:

- **Open-source gate - PASS**: MIT, SPDX trong source sở hữu, dependency inventory, không bundle dependency.
- **Human oversight - PASS**: AI recommendation tách khỏi decision; correction làm stale thay vì âm thầm đổi kết quả; không auto-reject.
- **Privacy - PASS**: synthetic data, blind projection, audit redacted, anonymization và PII scan.
- **Testability - PASS**: mỗi user story có independent journey; contract/unit/integration/component/E2E và benchmark gate.
- **Reproducibility - PASS**: immutable dataset/release lineage, offline fallback, clean-room verification và checksum.
- **Simplicity - PASS**: giữ single-node/SQLite, không thêm queue server; OCR optional, manual recovery bắt buộc.

Post-design check: PASS. Không còn `NEEDS CLARIFICATION`; không có constitution violation cần biện minh.

## Project Structure

### Documentation (this feature)

```text
specs/004-final-competition-release/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
├── contracts/
│   └── final-release-api.yaml
└── tasks.md                     # generated in the next workflow
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/                     # evaluation, correction, privacy, recovery endpoints
│   ├── core/                    # configuration, migrations, startup reconciliation
│   ├── models/                  # dataset runs, page map, corrections, leases, idempotency
│   ├── repositories/            # atomic claims, projections, evaluation persistence
│   ├── schemas/                 # request/response contracts
│   └── services/                # parsing, evidence, benchmark, recovery, privacy
├── evaluation/
│   ├── datasets/                # synthetic source/labels/manifests
│   └── reports/                 # generated and release-selected outputs
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    └── evaluation/

frontend/
├── src/
│   ├── components/recruiter/    # evidence navigation, corrections, privacy, recovery
│   ├── pages/
│   └── services/
└── tests/e2e/

scripts/
├── check_open_source_compliance.ps1
├── check_release_safety.ps1
├── run_ai_evaluation.ps1
└── verify_clean_room.ps1

docs/
├── AI_EVALUATION_REPORT.md
├── RELEASE_CHECKLIST.md
├── SHOWCASE.md
└── existing architecture/build/demo/privacy guides
```

**Structure Decision**: Mở rộng cấu trúc backend/frontend hiện tại theo từng domain nhỏ; dataset/report nằm ngoài runtime app nhưng dùng chung service đánh giá. Không tạo project hoặc infrastructure service mới.

## Delivery Strategy

### Milestone 0 - Freeze và baseline (13-15/09)

- Freeze feature scope, tạo tasks và traceability FR/SC.
- Tạo dataset manifest, label schema và 3 JD/30 CV synthetic tối thiểu.
- Chạy baseline bằng pipeline hiện tại; mở issue cho mọi metric fail.
- Chốt release threshold và demo claims; tuyệt đối không ghi target như result.

**Exit gate**: dataset review được, runner tính metric đúng bằng fixture nhỏ, baseline report có lineage.

### Milestone 1 - Evidence và human correction (16-19/09)

- Refactor parser thành page-aware extraction, backfill có chủ đích.
- Gắn page/source method vào evidence; điều hướng CV và fallback rõ.
- Thêm correction API/UI, validation, audit redaction và stale evaluation.
- Bổ sung contract, unit, integration, component và E2E.

**Exit gate**: 100% evidence test có page đúng hoặc location unknown; correction journey dưới 90 giây và không sửa lịch sử evaluation.

### Milestone 2 - Batch resilience và scan recovery (20-22/09)

- Persist idempotency cho create/retry/recover; payload conflict trả 409.
- Thêm processing lease, max attempts, expired-lease recovery và startup reconciliation.
- Hoàn chỉnh manual recovery cho `NEEDS_OCR`; đánh giá OCR adapter chỉ sau gate manual.
- Chạy kill/restart test trên lô mixed 200 CV.

**Exit gate**: zero lost/duplicate completed record; 10 replay tạo đúng một effect; mọi item kết thúc hoặc có recovery action.

### Milestone 3 - Responsible AI và final benchmark (23-24/09)

- Server-side blind projection cho list/detail/compare/evidence/export/filename.
- Reveal CV/PII theo role và audit; anonymization regression.
- Sửa pipeline theo issue baseline, chạy final offline và online benchmark.
- Review case false positive/false negative thủ công.

**Exit gate**: privacy matrix pass 100%; các metric đạt threshold hoặc claim/scope được điều chỉnh trung thực trước release.

### Milestone 4 - Release hardening (25-27/09)

- Sửa deprecation warning quan trọng và flake test; full CI hai lần.
- Sinh license/SBOM report, secret/PII scan và release manifest.
- Clean-room build từ source artifact ở đường dẫn mới trên Windows; xác nhận Linux CI.
- Test offline, cổng bị chiếm, missing model và crawler/Gemini failure.

**Exit gate**: toàn bộ automated gate xanh; clean-room dưới 30 phút; không secret/PII/generated output trong source release.

### Milestone 5 - Merge, release và showcase (28-29/09)

- Chia PR theo slice, review và merge vào `main`; không release từ feature branch.
- Cập nhật changelog/version, annotated tag và draft release.
- Đính kèm `.tar.gz`, SHA-256, SBOM/license, benchmark, screenshots/video và release notes.
- Diễn tập demo online/offline hai lượt, kiểm tra laptop/máy chiếu.
- Public release sau khi đối chiếu tag/commit/artifact.

**Exit gate**: 100% competition checklist có evidence; release public và clone được; demo 5-7 phút.

### Submission buffer (30/09)

- Chỉ sửa blocker dữ liệu/link; không thêm feature.
- Điền thông tin cá nhân/nhóm và form do người dự thi kiểm soát.
- Xác minh repository, release, demo và contact links ở chế độ không đăng nhập.

## Git Flow và Commit Plan

Không commit trực tiếp `main`. Từ commit tích hợp đã review, triển khai theo các branch ngắn; tên thực tế có thể dùng prefix `codex/` theo môi trường:

1. `feature/ai-evaluation-benchmark`
   - `test(ai): define versioned evaluation fixtures`
   - `feat(ai): generate reproducible quality report`
   - `docs(ai): publish measured evaluation results`
2. `feature/evidence-corrections`
   - `feat(parser): preserve page-aware resume sources`
   - `feat(recruiter): navigate and correct candidate evidence`
   - `test(recruiter): cover correction audit and stale scores`
3. `feature/batch-recovery`
   - `feat(batch): persist idempotent processing leases`
   - `feat(batch): recover interrupted and scanned resumes`
   - `test(batch): verify restart and replay safety`
4. `feature/blind-review`
   - `feat(privacy): add server-side blind review projections`
   - `test(privacy): prevent PII leakage across recruiter surfaces`
5. `release/v1.1.0-competition`
   - `chore(release): enforce final safety and license gates`
   - `docs(showcase): package competition evidence`
   - `chore(release): prepare v1.1.0 competition candidate`

Mỗi PR phải rebase/merge latest integration branch, có issue liên kết, acceptance evidence và CI xanh. Tag/release chỉ tạo sau merge vào `main` và xác nhận commit SHA.

## Quality Gates

### Gate A - Functional

- Five independent user journeys pass.
- Không regression bốn phân hệ hiện có.
- Offline fallback được thể hiện rõ trong UI.

### Gate B - AI evidence

- Dataset/labels được review, không PII.
- Metric report có formula, numerator/denominator, sample size và lineage.
- Threshold theo SC-003; nếu fail, release blocked.

### Gate C - Reliability/privacy

- Crash/replay/duplicate tests pass trên 200 item.
- Blind projection matrix và anonymization tests pass.
- Audit không chứa raw CV, evidence excerpt nhạy cảm, secret hoặc full PII.

### Gate D - Open source/release

- SPDX/license/dependency/SBOM scan pass.
- README/build/testing/AI/privacy/demo/release docs khớp hành vi thật.
- Source artifact/checksum/tag/commit khớp và clone clean-room thành công.
- Bug tracker có issue thực tế và lịch sử đóng lỗi.

## Risk Controls

| Risk | Trigger | Control / fallback |
|---|---|---|
| OCR làm hỏng clean-room | Cần binary/model hoặc accuracy thấp | Ship manual recovery; OCR experimental/disabled |
| Benchmark không đạt | Một metric dưới threshold | Triage case, sửa có regression; giảm claim chứ không sửa số |
| Batch recovery race | Duplicate CandidateResume hoặc stale worker commit | Unique/idempotency constraint + lease token + transaction |
| Blind review rò PII | PII xuất hiện ở một surface | Server projection matrix; release blocked |
| Evidence page sai | Ground truth khác page trả về | Unknown location, không suy đoán; regenerate page map |
| Deadline trễ | Milestone trễ > 1 ngày | Cắt OCR UI trước, giữ manual path; không cắt benchmark/release gate |
| Demo service ngoài lỗi | Gemini/crawler/model unavailable | Offline seed + deterministic fallback + video |
| Feature branch chưa vào main | HEAD không nằm trên default branch | Không tag/release; merge/retest first |

## Definition of Final

“100% để đi thi” chỉ được tuyên bố khi đồng thời:

1. SC-001 đến SC-013 có evidence;
2. full CI và clean-room pass trên commit release;
3. benchmark final đạt threshold và report trung thực;
4. repository/release công khai đáp ứng toàn bộ PoF;
5. demo online/offline hoàn thành hai lượt trong 5-7 phút;
6. không còn P0/P1 issue mở, secret, PII hoặc CV thật trong release;
7. tag và artifact trỏ đúng commit đã merge vào `main`.

## Complexity Tracking

Không có constitution violation. Các entity mới phục vụ trực tiếp reproducibility, audit và recovery; không thêm queue server, OCR bắt buộc hoặc project thứ ba.
