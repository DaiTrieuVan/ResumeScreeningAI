# Research: Final Competition Release

## 1. Đóng phạm vi theo giá trị chấm thi

**Decision**: Đóng băng các phân hệ mới. Final chỉ gồm benchmark AI, evidence theo trang và correction, batch recovery/idempotency, manual recovery cho CV scan, blind review và release/showcase.

**Rationale**: Các hạng mục này trực tiếp chứng minh mức hoàn thiện, usability, AI, tính nguyên gốc và PoF. Email, lịch phỏng vấn, chatbot hoặc ATS integration không cải thiện rủi ro quan trọng trước hạn nộp.

**Alternatives considered**: Mở rộng thành ATS đầy đủ; thêm chatbot; thêm nhiều dashboard. Đều bị loại vì tăng bề rộng nhưng làm giảm khả năng kiểm thử và tái tạo release.

## 2. Benchmark AI có thể tái hiện

**Decision**: Lưu dataset synthetic/ẩn danh và ground truth dưới dạng text/JSON nhỏ, review được bằng Git; runner tạo JSON máy đọc và Markdown cho showcase. Metric luôn kèm numerator, denominator, sample size, release SHA, dataset version, criteria version và AI mode.

**Rationale**: Định dạng mở, diff được và chạy offline. Một báo cáo có lineage rõ bảo vệ đội thi tốt hơn dashboard đẹp nhưng không tái hiện được. Metric classification/ranking phải được chọn theo nhiệm vụ và công thức phải công bố; hướng dẫn đánh giá của scikit-learn cũng nhấn mạnh lựa chọn scoring function theo bài toán ([official evaluation guide](https://scikit-learn.org/stable/modules/model_evaluation.html)).

**Alternatives considered**: Notebook thủ công; chỉ chụp screenshot; dùng dữ liệu CV thật. Notebook dễ lệch môi trường, screenshot không kiểm chứng được, CV thật tạo rủi ro PII.

## 3. Evidence theo trang và vị trí nguồn

**Decision**: Parser tạo text theo từng trang và page map với cumulative offsets. Evidence lưu page number bắt buộc khi match nằm trong page map; bounding box là tùy chọn. UI điều hướng PDF bằng page fragment, đồng thời hiển thị excerpt để fallback nếu browser không hỗ trợ định vị.

**Rationale**: `pdfplumber` hỗ trợ extract text theo page, word bounding boxes và search trả về tọa độ/characters, nên có thể tăng độ chính xác mà không đổi thư viện ([pdfplumber documentation](https://github.com/jsvine/pdfplumber)). Thư viện cũng ghi rõ hoạt động tốt nhất với PDF sinh từ máy, vì vậy scan phải có đường recovery riêng.

**Alternatives considered**: Suy ra page từ độ dài trung bình; OCR mọi PDF; dựng PDF viewer tùy biến. Suy ra page có thể tạo trích dẫn giả, OCR mọi file làm chậm pipeline, viewer mới quá lớn cho final.

## 4. Correction và stale evaluation

**Decision**: Correction là append-only event có old/new value đã redacted phù hợp, reason và actor. Candidate profile giữ giá trị hiệu lực; mọi correction liên quan scoring đặt evaluation thành stale và yêu cầu rerun có chủ đích.

**Rationale**: Không ghi đè lịch sử giúp human-in-the-loop có thể audit; không tự chạy lại tránh điểm thay đổi âm thầm trong lúc recruiter quyết định.

**Alternatives considered**: Cho sửa trực tiếp không audit; tự động chạy lại ngay. Cả hai làm giảm khả năng giải thích và tái hiện.

## 5. CV scan: manual recovery trước, OCR tùy chọn

**Decision**: Release bắt buộc có manual recovery: thay file hoặc nhập/xác nhận text có audit. OCR local là adapter feature-flag; chỉ đưa vào release nếu clean-room cài được và fixture Việt/Anh đạt threshold. OCR confidence thấp luôn về manual review.

**Rationale**: OCR native bổ sung binary/model và có thể phá tiêu chí build-from-source. Manual recovery bảo đảm mọi máy demo đều hoàn tất luồng. Tài liệu pdfplumber xác nhận giới hạn với scanned PDFs, nên đây là fallback có chủ đích chứ không che giấu lỗi.

**Alternatives considered**: Bắt buộc Tesseract cho mọi máy; gửi CV sang OCR cloud; từ chối mọi scan. Hai phương án đầu tăng dependency/quyền riêng tư, phương án cuối làm nghiệp vụ thiếu thực tế.

## 6. Batch recovery và idempotency trong phạm vi một máy

**Decision**: Giữ processing trên app cho bản thi nhưng thêm database lease, attempt limit, startup reconciliation và idempotency record có unique constraint. Worker chỉ claim item khi lease hết hạn/chưa tồn tại; commit hồ sơ và completion theo transaction. Không dùng `REPLACE` cho idempotency record.

**Rationale**: FastAPI cảnh báo `BackgroundTasks` không phù hợp heavy multi-process work và gợi ý queue ngoài cho quy mô lớn ([FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)). Bản thi là single-node/offline nên lease + recovery cho độ bền cần thiết mà không thêm Redis/RabbitMQ. SQLite hỗ trợ unique constraint và UPSERT/DO NOTHING cho xử lý conflict xác định ([SQLite UPSERT](https://www.sqlite.org/lang_upsert.html)).

**Alternatives considered**: Celery/Redis ngay; chỉ retry thủ công; giữ idempotency key nhưng bỏ qua. Hạ tầng queue làm clean-room khó hơn, hai phương án còn lại không bảo vệ duplicate/crash.

## 7. Blind review là projection, không phá dữ liệu gốc

**Decision**: Blind review áp dụng ở response/export projection dựa trên job setting và role; che cả tên file, evidence excerpt và free-text có PII. Mở CV gốc là thao tác reveal riêng có audit.

**Rationale**: Xóa/mutate dữ liệu nguồn làm mất audit và khó khôi phục. Projection cho phép cùng một hồ sơ phục vụ blind screening rồi mở danh tính ở giai đoạn hợp lệ.

**Alternatives considered**: Chỉ che tên trên bảng; tạo bản CV đã che vĩnh viễn; dựa hoàn toàn vào frontend. Các lựa chọn này dễ rò PII hoặc tạo hai nguồn sự thật.

## 8. Release và clean-room

**Decision**: Merge qua PR vào `main`, chạy full gate, tạo annotated semantic tag từ commit đã xác minh, phát hành draft trước khi public, kèm source `.tar.gz`, SHA-256, SBOM/license report, benchmark report và release notes. Clone artifact sang đường dẫn mới để kiểm tra offline.

**Rationale**: GitHub Releases gắn release với tag/target và hỗ trợ source archives/assets; draft cho phép hoàn thiện asset trước khi công khai ([GitHub release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)). Quy trình này tạo bằng chứng trực tiếp cho PoF và build-from-source.

**Alternatives considered**: Release trực tiếp từ feature branch; chỉ gắn tag; dùng ZIP/RAR làm artifact chính. Không đáp ứng release gate nội bộ hoặc làm bằng chứng PoF yếu.

## 9. Test và rollout

**Decision**: Mỗi slice có unit + contract + integration + component/E2E phù hợp; benchmark và release checks là gate riêng. Feature flag cho OCR và blind review trong quá trình hardening, nhưng cấu hình final phải được ghi trong release evidence.

**Rationale**: Tách slice giúp rollback và commit rõ, đồng thời tránh một thay đổi cuối làm hỏng toàn demo.

**Alternatives considered**: Chỉ manual test; một commit lớn; bật toàn bộ chức năng không có flag. Đều tăng rủi ro sát hạn.
