# Research: Recruiter Screening Workspace Upgrade

## 1. Criteria versioning và điểm chính thức

**Decision**: `ScreeningCriteriaSet` bất biến sau khi publish. Chỉnh sửa tạo draft/version mới. Mỗi `ScreeningEvaluation` pin đúng một version; thay slider chỉ tạo `ScoreSimulation`, không cập nhật evaluation.

**Rationale**: Hiện trọng số nằm trực tiếp trên JobPosting và UI tự tính “live score”, nên có thể hiển thị con số backend chưa từng đánh giá. Version bất biến giúp tái dựng quyết định và so sánh đúng chuẩn.

**Alternatives**: Ghi đè trọng số làm mất lịch sử; snapshot JSON trong từng result khó validate/query và dễ lệch schema.

## 2. Kết quả tiêu chí bốn trạng thái

**Decision**: Criterion có nhóm `MANDATORY/PREFERRED/BONUS`, operator và expected value. Kết quả dùng `MET/NOT_MET/UNKNOWN/NOT_APPLICABLE`; mandatory `NOT_MET` tạo cảnh báo loại, `UNKNOWN` yêu cầu kiểm tra.

**Rationale**: Thiếu dữ liệu không đồng nghĩa không đạt. Boolean hoặc văn bản tự do đều không đủ chính xác để lọc, so sánh và audit.

## 3. Upload batch và xử lý nền

**Decision**: POST upload tạo Batch/Items và trả `202 Accepted`; worker abstraction xử lý item độc lập với concurrency hữu hạn. MVP có thể chạy background task in-process, nhưng state nằm trong database để sau này thay bằng queue mà không đổi contract.

**Rationale**: Endpoint hiện xử lý tuần tự toàn bộ request. Persisted state giải quyết timeout, reload, retry và quan sát lỗi cấp tệp. Thêm Redis/Celery ngay là quá sớm cho quy mô MVP.

## 4. Dedupe nhiều lớp

**Decision**: Tính SHA-256 file, contact fingerprint chuẩn hóa và content fingerprint. Match lưu loại/confidence và mặc định `NEEDS_REVIEW`; không tự xóa.

**Rationale**: File giống hệt, CV cập nhật nhẹ và cùng người nộp nhiều lần là các tình huống khác nhau. Filename hoặc email đơn lẻ đều không đủ tin cậy.

## 5. Evidence-first evaluation

**Decision**: Mỗi `CriterionResult` liên kết 0..n `EvidenceSnippet` gồm excerpt, page/offset, polarity và confidence. Không có bằng chứng thì ghi rõ, không sinh trích dẫn giả.

**Rationale**: `ai_reasoning` hiện dễ đọc nhưng không kiểm chứng được; lưu toàn raw text trong result lại trùng dữ liệu và tăng rủi ro PII.

## 6. Truy vấn danh sách phía server

**Decision**: API hỗ trợ search, multi-filter, sort whitelist, pagination, facets và total. Saved View lưu cấu hình, không lưu snapshot kết quả.

**Rationale**: Frontend hiện fetch/filter/paginate client-side, không phù hợp 500–1.000 hồ sơ hoặc selection nhiều trang. Search engine riêng chưa cần ở quy mô này.

## 7. Bulk action idempotent

**Decision**: Bulk request nhận selection expression hoặc ID, `idempotency_key`, expected version và action payload. Response có summary và kết quả từng item; partial success không được báo như thành công toàn phần.

**Rationale**: Preview phạm vi, idempotency và optimistic concurrency ngăn click lại hoặc ghi đè thay đổi của recruiter khác.

## 8. Pipeline, decision và audit

**Decision**: `RecruitmentDecisionEvent` append-only là lịch sử; CandidateApplication giữ projection để đọc nhanh. AI recommendation bất biến, human decision lưu riêng, reject bắt buộc reason code.

**Rationale**: Một status mutable và note bị ghi đè không giải thích được ai quyết định gì, khi nào. Event sourcing toàn hệ thống không cần thiết; chỉ event hóa decision workflow.

## 9. Privacy và retention

**Decision**: Xem/tải/xuất CV phải audit; file gốc chỉ qua endpoint kiểm quyền. Anonymization xóa PII và file nhưng giữ aggregate/audit tối thiểu không chứa raw CV.

**Rationale**: CV chứa dữ liệu cá nhân; đường dẫn lưu trữ server không được lộ trực tiếp cho client.

## 10. Rollout

**Decision**: Backfill dữ liệu legacy, duy trì API cũ trong một release và bật workspace v2 bằng feature flag; không big-bang rewrite.

**Rationale**: Cho phép so sánh/rollback và không ảnh hưởng Real Jobs hay Career Gap Advisor.
