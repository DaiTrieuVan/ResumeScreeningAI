# Quickstart Validation: Final Competition Release

## Mục tiêu

Chứng minh bản dự thi có thể build từ source, đo AI bằng số liệu thật, kiểm chứng/correct evidence, phục hồi batch, blind review và chạy demo offline. Chỉ đánh dấu release-ready khi mọi expected result dưới đây đạt.

## Prerequisites

- Checkout commit ứng viên phát hành trên nhánh tích hợp.
- Python 3.10+, Node.js 18+, Git; không tái sử dụng `venv`, `node_modules` hoặc database cũ.
- Dataset synthetic final tối thiểu 30 CV, 3 JD và manifest đã review.
- Không đặt Gemini key cho lượt offline đầu tiên.

## 1. Baseline quality gate

```powershell
.\scripts\check_open_source_compliance.ps1
cd backend
python -m pytest -q
cd ..\frontend
npm ci
npm test -- --run
npm run build
npm run test:e2e
```

**Expected**: tất cả lệnh exit 0; không có secret, PII, CV thật, database hoặc generated output bị track. Test report ghi số test và commit SHA.

## 2. Benchmark AI

Chạy evaluation runner với dataset published ở hai chế độ:

1. deterministic/offline fallback;
2. cấu hình AI showcase nếu có network/key.

**Expected**:

- Báo cáo JSON và Markdown chứa lineage đầy đủ.
- Dataset >= 30 CV, >= 3 JD.
- Mandatory recall >= 0,90.
- Evidence precision >= 0,90.
- UNKNOWN accuracy >= 0,95.
- Ranking agreement >= 0,70.
- Không metric nào có denominator 0 hoặc bị thay bằng target.

Nếu một threshold fail, release dừng; mở issue kèm case IDs gây lỗi.

## 3. Evidence và correction journey

1. Tạo job/criteria published từ fixture.
2. Upload CV native nhiều trang và chạy screening.
3. Mở Candidate Review, chọn ít nhất ba evidence ở các trang khác nhau.
4. Xác nhận CV chuyển đúng trang hoặc hiển thị fallback rõ khi vị trí chưa biết.
5. Sửa một extracted skill/experience với reason.
6. Reload detail và timeline.

**Expected**: page number đúng ground truth; correction được audit; historical evaluation không bị sửa; evaluation hiện tại được đánh dấu stale và chỉ hết stale sau rerun.

## 4. Scan/manual recovery journey

1. Upload PDF scan không có text.
2. Xác nhận item ở `NEEDS_OCR`/manual-review, không bị coi là CV không đạt.
3. Cung cấp verified text hoặc replacement PDF.
4. Tiếp tục xử lý và mở evidence.

**Expected**: source method hiển thị MANUAL/OCR; confidence thấp không tạo quyết định chắc chắn; raw verified text không xuất hiện trong audit log.

## 5. Crash recovery và idempotency

1. Tạo batch mixed 200 item.
2. Dừng backend khi còn item processing, sau đó khởi động lại.
3. Gọi recover với cùng idempotency key 10 lần.
4. Gọi lại key đó với payload khác để kiểm tra conflict.

**Expected**: không mất completed item, không tạo duplicate CandidateResume, request giống trả cùng kết quả, payload khác nhận 409, mọi item kết thúc hoặc có retry/manual action rõ.

## 6. Blind review và privacy

1. Bật BLIND cho job demo.
2. Kiểm tra candidate list, detail, comparison, evidence, filename và export.
3. Thử truy cập CV gốc bằng role không hợp lệ.
4. Reveal bằng role hợp lệ rồi kiểm tra audit.
5. Anonymize một hồ sơ fixture.

**Expected**: không PII rò ở bất kỳ surface blind nào; access sai bị từ chối; reveal được audit; anonymization xóa file và dữ liệu dẫn xuất nhạy cảm.

## 7. Clean-room release rehearsal

1. Tạo source `.tar.gz` và SHA-256 từ commit candidate.
2. Giải nén vào đường dẫn mới có khoảng trắng và ký tự tiếng Việt.
3. Làm đúng `docs/BUILD_AND_DEPLOYMENT.md` từ đầu.
4. Chạy health check và toàn bộ demo offline.
5. Đối chiếu checksum, version và commit.

**Expected**: hoàn tất trong dưới 30 phút, không sửa source, không cần service nguồn đóng, UI/API chạy ngoài checkout gốc.

## 8. Showcase rehearsal

- Chạy kịch bản 5-7 phút theo `docs/DEMO_GUIDE.md`.
- Mở video offline dự phòng.
- Kiểm tra laptop, máy chiếu, font, zoom, cổng và notification.
- Chỉ trình bày metric từ báo cáo final.

**Expected**: hai lượt liên tiếp hoàn thành đúng thời lượng; người xem hiểu bài toán, AI evidence, human decision, fallback và điểm khác biệt mà không cần giải thích ngoài kịch bản.

## Final evidence record

Ghi vào release manifest: tag/version, commit SHA, checksums, CI URL, test counts, benchmark run/dataset, clean-room verifier/date, demo video/screenshots và trạng thái từng mục checklist PoF.
