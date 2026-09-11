# Quickstart & Acceptance Guide

## Purpose

Tiêu chuẩn triển khai và nghiệm thu cho Recruiter Workspace v2. Đây chưa phải hướng dẫn của tính năng đã hoàn thành.

## Local prerequisites

- Python 3.10+, Node.js 18+
- Backend config/API key hiện có nếu chạy đánh giá thật
- Một bản sao database hiện tại để kiểm tra migration

## Baseline commands

```powershell
cd "D:\Resume Screening AI Project\backend"
python -m pytest

cd "D:\Resume Screening AI Project\frontend"
npm install
npm run build
```

Khi thêm test frontend, chuẩn hóa `npm test` và `npm run test:e2e`.

## Migration verification

1. Sao chép database development có dữ liệu cũ.
2. Chạy migration mới hai lần để xác nhận idempotent.
3. Kiểm tra mỗi job cũ có Criteria version 1 và mỗi result cũ có Evaluation legacy.
4. Xác nhận CV cũ vẫn mở đúng; legacy result ghi “chưa có bằng chứng nguồn”.
5. Chạy test cũ để xác nhận compatibility.

## Journey A — Criteria và evidence

1. Tạo job Backend Engineer với mandatory Python/3 năm kinh nghiệm, preferred FastAPI/PostgreSQL, bonus Docker.
2. Publish với tổng trọng số 95%: hệ thống phải chặn và chỉ rõ thiếu 5%.
3. Publish version 1 đủ 100%, upload hai CV và chạy official evaluation.
4. Thay slider nhưng không publish: danh sách phải ghi “Mô phỏng”, điểm chính thức không đổi.
5. Mở detail: mỗi criterion có MET/NOT_MET/UNKNOWN/N/A và evidence mở đúng vị trí CV.
6. Publish version 2: evaluation v1 được đánh dấu cũ, không âm thầm tính lại.

**Expected**: Không có điểm chính thức thiếu criteria version; không có kết luận quan trọng giả vờ có bằng chứng.

## Journey B — Batch 200 CV

Chuẩn bị 200 mục gồm PDF hợp lệ, duplicate exact/contact, PDF hỏng, password và PDF ảnh.

1. Upload vào một batch rồi reload trang.
2. Xác nhận tiến độ từng item tiếp tục cập nhật và lỗi không dừng file hợp lệ.
3. Giải quyết duplicate bằng Keep both/Link existing/Skip.
4. Chọn Retry failed; chỉ item lỗi tăng attempt và chạy lại.

**Expected**: Counts nhất quán; không mất kết quả thành công; retry không tạo application ngoài ý muốn.

## Journey C — Triage và quyết định

1. Với 500 ứng viên, lọc mandatory passed + Python + điểm >=70 + chưa review; sort score giảm dần.
2. Lưu view, chọn 20 ứng viên qua nhiều trang.
3. Preview bulk action, chuyển sang Recruiter Review và gắn tag ưu tiên.
4. Compare ba người; xác nhận cùng criteria version và UNKNOWN không hiển thị là fail.
5. Shortlist một người; reject một người với reason bắt buộc.
6. Kiểm tra timeline có actor/time/before/after và AI recommendation gốc.

**Expected**: Triage dưới 3 phút; decision truy vết được; partial bulk failure hiển thị từng item.

## Non-functional checks

- Query 1.000 ứng viên p95 dưới 1 giây; bulk 50 ứng viên dưới 30 giây.
- Keyboard-only hoàn tất lọc, chọn hàng, mở drawer và đổi stage.
- Viewport 1366×768 và tablet không che CTA quan trọng.
- Hai phiên cùng update: phiên sau nhận 409 và được yêu cầu refresh/merge.
- Người không có quyền không xem/tải CV; download/export tạo audit event.

## Definition of Done per slice

- Migration và restore procedure được kiểm chứng.
- Contract, unit, integration, UI tests đều xanh.
- Empty/loading/error/partial-success state có test.
- Không log raw CV, email, phone hoặc evidence không cần thiết.
- Có telemetry latency, failure, retry, override và conflict.
- Release note nêu compatibility và feature flag.
