# Feature Specification: Final Competition Release

**Feature Branch**: `docs/competition-documentation`

**Created**: 2026-09-13

**Status**: Draft

**Input**: User description: "Hoàn thiện phiên bản cuối Resume Screening AI để đạt release gate cuộc thi: benchmark AI có số liệu, evidence điều hướng đúng trang và chỉnh sửa có audit, OCR hoặc manual recovery, batch idempotency và crash recovery, blind review, bảo mật dữ liệu demo, clean-room build, tài liệu showcase và phát hành mã nguồn mở."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chứng minh chất lượng AI bằng số liệu (Priority: P1)

Là đội thi, tôi muốn chạy một bộ đánh giá có đáp án chuẩn và nhận báo cáo có thể tái hiện, để chứng minh các kết luận, bằng chứng và thứ hạng của AI đạt chất lượng đo được thay vì chỉ trình diễn cảm tính.

**Why this priority**: Khả năng tích hợp AI chiếm điểm riêng và là phần dễ bị phản biện nhất. Không có kết quả thực đo, đội thi không thể bảo vệ độ tin cậy của sản phẩm.

**Independent Test**: Chạy bộ đánh giá đã khóa phiên bản, xác nhận báo cáo ghi đủ dữ liệu, cỡ mẫu, phiên bản tiêu chí, cấu hình AI, thời gian chạy và các chỉ số bắt buộc; chạy lại cùng cấu hình cho kết quả nằm trong sai số công bố.

**Acceptance Scenarios**:

1. **Given** bộ CV/JD tổng hợp đã có đáp án chuẩn, **When** đội thi chạy đánh giá, **Then** hệ thống xuất mandatory recall, evidence precision, UNKNOWN accuracy, ranking agreement và batch completion với tử số, mẫu số và cỡ mẫu.
2. **Given** một kết quả đánh giá, **When** người xem mở báo cáo, **Then** có thể xác định phiên bản sản phẩm, dữ liệu, tiêu chí, prompt/model và chế độ online/offline đã tạo kết quả.
3. **Given** chỉ số chưa đạt ngưỡng công bố, **When** tạo báo cáo, **Then** báo cáo thể hiện thất bại rõ ràng và không thay mục tiêu thành kết quả thực đo.

---

### User Story 2 - Kiểm chứng và sửa kết quả trên CV gốc (Priority: P1)

Là recruiter, tôi muốn bấm vào bằng chứng để đến đúng trang CV và sửa dữ liệu trích xuất sai với lịch sử thay đổi, để quyết định cuối cùng dựa trên nguồn có thể kiểm tra.

**Why this priority**: Evidence-first và human-in-the-loop là khác biệt cốt lõi của sản phẩm; nếu trích dẫn không dẫn được tới nguồn hoặc không sửa được lỗi, khác biệt này chưa hoàn chỉnh.

**Independent Test**: Mở một ứng viên có bằng chứng ở nhiều trang, điều hướng từ ba kết luận đến đúng trang, sửa một trường trích xuất và xác nhận điểm liên quan được đánh dấu cần đánh giá lại cùng audit event.

**Acceptance Scenarios**:

1. **Given** một criterion có evidence xác định được vị trí, **When** recruiter chọn evidence, **Then** CV mở đúng trang và đoạn liên quan được làm nổi bật hoặc định vị rõ.
2. **Given** evidence không có vị trí trang đáng tin cậy, **When** hiển thị kết quả, **Then** giao diện ghi rõ giới hạn và vẫn cho phép tìm đoạn văn trong CV.
3. **Given** recruiter sửa kỹ năng, kinh nghiệm hoặc thông tin liên hệ bị trích xuất sai, **When** lưu, **Then** hệ thống ghi giá trị cũ, giá trị mới, người sửa, thời gian và đánh dấu evaluation bị ảnh hưởng là stale.

---

### User Story 3 - Phục hồi CV khó đọc và batch bị gián đoạn (Priority: P1)

Là recruiter xử lý nhiều CV, tôi muốn có đường khắc phục cho PDF scan và lô xử lý bị dừng, để không phải tải lại toàn bộ hoặc mất kết quả đã thành công.

**Why this priority**: Demo hàng loạt chỉ thuyết phục khi lỗi tệp và lỗi tiến trình đều có thể phục hồi an toàn.

**Independent Test**: Tải một lô gồm PDF chữ, PDF scan, tệp lỗi và tệp trùng; dừng tiến trình giữa chừng rồi khởi động lại; xác nhận kết quả đã hoàn tất không bị nhân đôi và mọi item còn lại có trạng thái/hành động rõ ràng.

**Acceptance Scenarios**:

1. **Given** PDF không có lớp chữ, **When** parser không đọc được, **Then** item chuyển sang trạng thái cần OCR hoặc nhập/xác nhận thủ công thay vì lỗi chung.
2. **Given** backend bị dừng khi batch đang chạy, **When** hệ thống hoạt động lại, **Then** item dở dang được phục hồi hoặc trả về trạng thái retry an toàn mà không nhân đôi hồ sơ.
3. **Given** cùng một yêu cầu retry được gửi lại, **When** khóa idempotency trùng, **Then** chỉ một lần xử lý có hiệu lực và người dùng nhận cùng kết quả nghiệp vụ.
4. **Given** một item thất bại lặp lại, **When** vượt giới hạn retry, **Then** hệ thống dừng tự động, lưu nguyên nhân cuối và đưa ra hành động thủ công.

---

### User Story 4 - Sàng lọc giảm thiên lệch và bảo vệ dữ liệu demo (Priority: P2)

Là hiring manager, tôi muốn bật chế độ blind review và kiểm soát vòng đời dữ liệu, để đánh giá ban đầu tập trung vào tiêu chí nghề nghiệp và demo không làm lộ dữ liệu cá nhân.

**Why this priority**: Tính có trách nhiệm làm tăng giá trị nguyên gốc và khả năng bảo vệ sản phẩm trước câu hỏi về bias, quyền riêng tư và auto-reject.

**Independent Test**: Bật blind review, xác nhận danh sách/detail/compare/export ẩn các trường nhận diện; sau đó khôi phục quyền xem có audit và chạy xóa/ẩn danh hồ sơ demo theo chính sách.

**Acceptance Scenarios**:

1. **Given** blind review đang bật, **When** người dùng xem hoặc so sánh ứng viên, **Then** tên, email, điện thoại, ảnh, địa chỉ và các trường nhận diện được ẩn nhất quán.
2. **Given** người dùng có quyền cần xem PII, **When** tắt blind review hoặc mở CV gốc, **Then** hành động được ghi audit mà không ghi nội dung CV vào log.
3. **Given** hồ sơ hết hạn lưu hoặc có yêu cầu xóa, **When** thực hiện anonymization, **Then** file gốc và dữ liệu dẫn xuất nhạy cảm bị loại bỏ trong khi audit nghiệp vụ tối thiểu không chứa PII được giữ lại.

---

### User Story 5 - Phát hành và trình diễn bản dự thi có thể tái tạo (Priority: P1)

Là đội thi và giám khảo, tôi muốn clone đúng bản phát hành, làm theo tài liệu và chạy được demo đầy đủ kể cả khi mất Internet, để sản phẩm đáp ứng tiêu chí mã nguồn mở và không phụ thuộc máy phát triển.

**Why this priority**: Release, build from source, tài liệu và showcase chiếm phần lớn điểm PoF và quyết định mức hoàn thiện trong vòng chung kết.

**Independent Test**: Trên thư mục sạch, clone source từ release, cấu hình bằng tệp mẫu, chạy test/build, thực hiện kịch bản recruiter bằng dữ liệu synthetic, ngắt dịch vụ ngoài và hoàn thành lại hành trình bằng fallback.

**Acceptance Scenarios**:

1. **Given** một máy sạch đáp ứng prerequisites, **When** làm đúng hướng dẫn release, **Then** backend, frontend, test và demo khởi chạy mà không sửa mã nguồn.
2. **Given** Gemini, model download hoặc crawler không khả dụng, **When** chạy demo offline, **Then** hành trình chính vẫn hoàn tất và giao diện cho biết đang dùng fallback.
3. **Given** repository release công khai, **When** giám khảo kiểm tra, **Then** tìm thấy license, SPDX, changelog, bug tracker, dependency/license report, source artifact mở, checksum, hướng dẫn build và showcase.
4. **Given** kịch bản trình bày 5-7 phút, **When** đội thi diễn tập, **Then** hoàn thành đúng thời lượng và chứng minh được bài toán, AI, evidence, human decision, fallback và giá trị khác biệt.

### Edge Cases

- CV scan nhiều trang, xoay trang, chữ tiếng Việt/Anh trộn lẫn hoặc OCR có confidence thấp.
- Evidence xuất hiện nhiều lần; offset thay đổi sau khi text được chuẩn hóa hoặc recruiter chỉnh dữ liệu.
- Correction làm thay đổi kết quả mandatory gate hoặc thứ hạng khi criteria version cũ vẫn đang được xem.
- Batch dừng sau khi lưu file nhưng trước khi commit hồ sơ; hai worker cùng nhận một item; retry đến sau khi item đã hoàn tất.
- Blind review vẫn có tên riêng trong evidence, ghi chú, tên file, lịch sử công ty hoặc CV viewer.
- Bộ benchmark thiếu nhãn, nhãn mâu thuẫn giữa hai người chấm hoặc sample quá nhỏ để công bố.
- Máy demo mất mạng, chưa tải model, cổng mặc định bị chiếm hoặc đường dẫn source chứa dấu/khoảng trắng.
- Release tag không trỏ tới commit trên default branch hoặc artifact/checksum không khớp.
- Dữ liệu thật, secret, database, export hoặc video có PII vô tình xuất hiện trong commit/release.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Hệ thống MUST cung cấp bộ dữ liệu đánh giá tổng hợp hoặc đã ẩn danh với đáp án chuẩn, phiên bản và hướng dẫn gán nhãn.
- **FR-002**: Quy trình đánh giá MUST tính mandatory recall, evidence precision, UNKNOWN accuracy, ranking agreement và batch completion từ dữ liệu thực đo.
- **FR-003**: Mỗi báo cáo đánh giá MUST ghi phiên bản sản phẩm, dataset, criteria, prompt/model, chế độ fallback, cỡ mẫu, ngày đo và công thức chỉ số.
- **FR-004**: Mục tiêu chất lượng và kết quả thực đo MUST được trình bày tách biệt; báo cáo MUST fail rõ nếu thiếu dữ liệu hoặc không đạt release threshold.
- **FR-005**: Evidence MUST lưu vị trí nguồn theo trang khi parser xác định được và MUST không tạo số trang giả khi không xác định được.
- **FR-006**: Người dùng MUST có thể điều hướng từ criterion result đến evidence trong CV gốc mà không mất ngữ cảnh ứng viên.
- **FR-007**: Người dùng có quyền MUST có thể sửa dữ liệu trích xuất và bổ sung/xác nhận evidence với lý do.
- **FR-008**: Correction MUST tạo audit event và MUST đánh dấu evaluation/score chịu ảnh hưởng là stale cho tới khi được đánh giá lại.
- **FR-009**: PDF không có lớp chữ MUST có trạng thái riêng và đường khắc phục bằng OCR hoặc nhập/xác nhận thủ công.
- **FR-010**: Kết quả OCR confidence thấp MUST chuyển sang manual review và MUST NOT tự động trở thành bằng chứng chắc chắn.
- **FR-011**: Batch processing MUST phục hồi item bị gián đoạn sau restart, giữ kết quả đã hoàn tất và không tạo hồ sơ trùng.
- **FR-012**: Các thao tác tạo batch, retry và phục hồi MUST thực thi idempotent theo khóa yêu cầu được lưu bền vững.
- **FR-013**: Retry MUST có giới hạn, backoff và lỗi cuối dễ hiểu; chi tiết kỹ thuật không được chứa raw CV hoặc secret.
- **FR-014**: Blind review MUST ẩn nhất quán PII trên list, detail, compare, export, evidence và tên file trước vòng quyết định được cấu hình.
- **FR-015**: Mở khóa PII hoặc CV gốc MUST yêu cầu quyền phù hợp và tạo audit event.
- **FR-016**: Hệ thống MUST hỗ trợ xóa hoặc ẩn danh dữ liệu ứng viên demo mà không giữ PII trong dữ liệu dẫn xuất hay log.
- **FR-017**: AI MUST chỉ đưa recommendation; không hành động auto-reject hoặc auto-hire trong bản dự thi.
- **FR-018**: Bản phát hành dự thi MUST được tạo từ default branch sau khi toàn bộ quality gate thành công.
- **FR-019**: Release MUST có version, changelog, source artifact định dạng mở, checksum và tài liệu build/run/test độc lập với máy phát triển.
- **FR-020**: Repository công khai MUST có license OSI-approved, SPDX trong mã nguồn sở hữu, dependency/license inventory, bug tracker có lịch sử sử dụng và hướng dẫn đóng góp.
- **FR-021**: Release gate MUST chặn secret, PII, CV thật, database, generated output và artifact nhạy cảm bị track.
- **FR-022**: Demo package MUST dùng dữ liệu synthetic, có kịch bản 5-7 phút, video offline, ảnh chụp và phương án fallback không cần dịch vụ ngoài.
- **FR-023**: Clean-room validation MUST chứng minh cài đặt, build, test và chạy demo được từ release source trong một đường dẫn mới.
- **FR-024**: Giao diện MUST hiển thị rõ model/fallback mode, trạng thái thiếu dữ liệu và cảnh báo AI chỉ hỗ trợ quyết định.
- **FR-025**: Mọi lỗi phát hiện trong final hardening MUST có regression test hoặc bước tái hiện được ghi trong bug tracker trước khi đóng.

### Key Entities

- **Evaluation Dataset**: Bộ JD, CV synthetic/ẩn danh, nhãn chuẩn, người/qui trình gán nhãn, phiên bản và phạm vi sử dụng.
- **Evaluation Run**: Một lần đo gắn với release, dataset, criteria, AI configuration, thời gian, trạng thái và các metric.
- **Metric Result**: Chỉ số có công thức, tử số, mẫu số, giá trị, ngưỡng và trạng thái pass/fail.
- **Source Location**: Vị trí evidence gồm tài liệu, trang, offsets, excerpt và confidence; có thể biểu diễn vị trí chưa xác định.
- **Candidate Correction**: Giá trị cũ/mới, trường bị sửa, lý do, actor, thời gian và evaluation bị ảnh hưởng.
- **Processing Lease**: Quyền xử lý tạm thời của một item, gồm owner, thời hạn, attempt và trạng thái phục hồi.
- **Idempotency Record**: Khóa yêu cầu, phạm vi thao tác, fingerprint, kết quả và thời hạn giữ để chống xử lý lặp.
- **Review Privacy Mode**: Chính sách blind review theo job/session và phạm vi trường phải ẩn.
- **Release Evidence**: Version, commit, tag, checksum, test report, license report, artifact và clean-room verification record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% kết quả benchmark công bố truy ngược được tới release, dataset, criteria và cấu hình AI cụ thể.
- **SC-002**: Bộ benchmark cuối có tối thiểu 30 CV synthetic/ẩn danh, ít nhất 3 JD và bao phủ hồ sơ đạt, không đạt, thiếu dữ liệu, trùng, scan và lỗi.
- **SC-003**: Mandatory recall và evidence precision thực đo đều đạt ít nhất 90%; UNKNOWN accuracy đạt ít nhất 95%; ranking agreement đạt ít nhất 0,70.
- **SC-004**: 100% evidence có page location hợp lệ hoặc trạng thái vị trí chưa xác định; không có trích dẫn trang giả.
- **SC-005**: Recruiter có thể kiểm chứng và sửa một kết luận sai trong dưới 90 giây; 100% correction được audit và đánh dấu stale đúng phạm vi.
- **SC-006**: Trong bài test restart trên lô 200 CV, không mất kết quả đã hoàn tất, không tạo hồ sơ trùng và 100% item về trạng thái kết thúc hoặc retry rõ ràng.
- **SC-007**: Gửi lặp cùng thao tác idempotent 10 lần chỉ tạo một thay đổi nghiệp vụ.
- **SC-008**: Blind review che toàn bộ trường nhận diện đã định nghĩa trong list, detail, compare, export và evidence ở 100% test fixture.
- **SC-009**: Một người mới có thể clone release vào thư mục sạch và hoàn tất build/test/demo bằng tài liệu trong dưới 30 phút, không sửa source.
- **SC-010**: Backend, frontend component, E2E, compliance, secret/PII scan và production build đều pass trên commit phát hành.
- **SC-011**: Demo chính hoàn tất trong 5-7 phút ở cả online và offline mode; video dự phòng mở được trên laptop trình chiếu.
- **SC-012**: 100% mục PoF trong checklist cuộc thi có bằng chứng công khai hoặc biên bản xác minh trước khi nộp.
- **SC-013**: Ít nhất 85% người thử nghiệm không cần hỗ trợ để hoàn thành upload batch, kiểm chứng evidence, sửa dữ liệu và shortlist một ứng viên.

## Assumptions

- Phạm vi final tập trung vào Recruiter Workspace, AI quality, responsible AI, độ bền demo và phát hành; không thêm email, lịch phỏng vấn, chatbot hoặc tích hợp ATS.
- Dữ liệu benchmark và demo chỉ dùng dữ liệu synthetic hoặc đã được xác nhận ẩn danh; không dùng CV thật chưa có đồng ý.
- OCR local là lựa chọn ưu tiên; nếu không đạt độ ổn định trong thời gian final, manual recovery hoàn chỉnh là tiêu chí bắt buộc còn OCR được gắn nhãn thử nghiệm.
- Blind review phục vụ vòng sàng lọc ban đầu và không thay thế cơ chế authentication/RBAC production.
- Bản thi chạy được hoàn toàn offline; Gemini và live crawler là khả năng tăng cường, không phải dependency bắt buộc.
- SQLite và worker trong một máy phù hợp demo; production multi-user, multi-node, SSO, malware scanning và encryption infrastructure nằm ngoài phạm vi cuộc thi nhưng phải được ghi rõ.
- Không tuyên bố “production-ready” nếu các kiểm soát production trong tài liệu privacy chưa được triển khai.
- Default branch và release chỉ được cập nhật sau review; kế hoạch này không tự động merge, tag, push hoặc publish.
