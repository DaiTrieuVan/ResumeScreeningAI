# Testing Guide

## Test pyramid

- Backend unit tests kiểm tra scoring, criteria, evidence, upload state và privacy.
- Contract tests kiểm tra response shape và hành vi API.
- Integration tests kiểm tra migration, query, batch, bulk, decision và analytics.
- Frontend component tests kiểm tra state, validation và interaction.
- Playwright E2E kiểm tra hành trình recruiter ở browser thực.

## Chạy toàn bộ

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm test -- --run
npm run test:e2e
npm run build
```

Test backend đặt `DISABLE_EMBEDDING_MODEL=true` qua `tests/conftest.py`, tránh tải
model trong test discovery. Test embedding chuyên biệt inject model xác định.

## Acceptance journeys

1. Criteria version, weight validation, official/simulation và evidence.
2. Batch upload gồm PDF hợp lệ, duplicate, file lỗi và retry.
3. Triage, cross-page selection, compare, decision, conflict và timeline.

Chi tiết dữ liệu và expected result ở
`specs/003-recruiter-workspace-upgrade/quickstart.md`.

## Nguyên tắc fixture

- Không sử dụng CV thật hoặc dữ liệu cá nhân.
- External AI, crawler và network phải mock/fallback trong automated tests.
- Mỗi bug fix cần regression test thất bại trước khi sửa.
- Không giảm assertion chỉ để làm test xanh.

## Release gate

Release bị chặn nếu có test fail, production build fail, migration không idempotent,
secret/PII bị track hoặc dependency license chưa được đánh giá.

GitHub Actions chạy compliance, backend, frontend component, build và Playwright
trên pull request. Có thể chạy riêng kiểm tra hồ sơ mã nguồn mở bằng:

```powershell
.\scripts\check_open_source_compliance.ps1
```

Gate bản dự thi còn chạy kiểm tra release-safety và benchmark xác định trong chế
độ offline. Job Windows cuối cùng dựng source archive ở đường dẫn mới, cài lại
dependency rồi chạy toàn bộ backend, frontend, build và E2E:

```powershell
.\scripts\check_release_safety.ps1
.\scripts\run_ai_benchmark.ps1
.\scripts\verify_clean_room.ps1 -SourceMode Archive -RecordPath release\clean-room-result.json
```

Hành trình `competition-showcase.spec.js` mock biên mạng nhưng đi xuyên qua ba
module Jobs, Recruiter và Gap Advisor. Kết quả đo, checksum và giới hạn diễn giải
được lưu tại `docs/AI_EVALUATION.md` và `release/verification-record.md`.
