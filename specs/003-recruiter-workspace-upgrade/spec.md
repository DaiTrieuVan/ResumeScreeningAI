# Feature Specification: Recruiter Screening Workspace Upgrade

**Feature Branch**: `codex/light-professional-ui`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Nâng cấp Không gian tuyển dụng để nhà tuyển dụng có thể tải số lượng lớn CV, đánh giá độ phù hợp với công việc nhanh, đáng tin cậy và thuận tiện hơn."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Thiết lập tiêu chí sàng lọc đáng tin cậy (Priority: P1)

Là nhà tuyển dụng, tôi muốn phân loại yêu cầu của vị trí thành tiêu chí bắt buộc, ưu tiên và cộng điểm; đồng thời cấu hình trọng số có tổng bằng 100%, để điểm AI phản ánh đúng chính sách tuyển dụng và không che khuất điều kiện loại trực tiếp.

**Why this priority**: Mọi kết quả xếp hạng phía sau đều phụ thuộc vào cấu hình này. Sai lệch giữa cấu hình hiển thị và cấu hình thực thi làm mất niềm tin vào toàn bộ hệ thống.

**Independent Test**: Tạo một vị trí có hai tiêu chí bắt buộc và ba tiêu chí ưu tiên, thay đổi trọng số rồi chạy sàng lọc; xác nhận hệ thống chỉ chấp nhận tổng 100%, lưu phiên bản cấu hình và gắn cờ ứng viên vi phạm tiêu chí bắt buộc dù điểm tổng cao.

**Acceptance Scenarios**:

1. **Given** nhà tuyển dụng đang cấu hình ba nhóm trọng số, **When** tổng khác 100%, **Then** hệ thống hiển thị chênh lệch, không cho lưu cấu hình chính thức và hướng dẫn cách cân bằng.
2. **Given** cấu hình đã lưu, **When** nhà tuyển dụng thay đổi slider để thử nghiệm, **Then** hệ thống phân biệt rõ điểm mô phỏng với điểm chính thức và yêu cầu lưu/chạy lại trước khi thay thế kết quả chính thức.
3. **Given** ứng viên đạt điểm tổng cao nhưng thiếu một tiêu chí bắt buộc, **When** kết quả được hiển thị, **Then** ứng viên có cảnh báo rõ ràng và không tự động được đưa vào shortlist.

---

### User Story 2 - Tiếp nhận hàng loạt CV an toàn và có thể phục hồi (Priority: P1)

Là nhà tuyển dụng, tôi muốn tải hàng trăm CV trong một phiên và theo dõi trạng thái từng tệp, để lỗi ở một CV không làm dừng cả lô và tôi có thể xử lý lại các hồ sơ lỗi hoặc trùng lặp.

**Why this priority**: Khả năng xử lý khối lượng lớn là giá trị vận hành cốt lõi của sản phẩm.

**Independent Test**: Tải một lô gồm CV hợp lệ, CV trùng, PDF hỏng và PDF ảnh; xác nhận mỗi tệp có trạng thái riêng, bản trùng được phát hiện, lỗi không dừng lô và các mục lỗi có thể chạy lại.

**Acceptance Scenarios**:

1. **Given** lô CV có tệp hợp lệ và không hợp lệ, **When** xử lý diễn ra, **Then** tiến độ tổng và trạng thái từng tệp được cập nhật độc lập.
2. **Given** hai CV có cùng thông tin liên hệ hoặc nội dung gần trùng, **When** tệp thứ hai được tải lên, **Then** hệ thống cảnh báo trùng và cho phép giữ, thay thế hoặc bỏ qua mà không tự ý xóa dữ liệu.
3. **Given** một số CV xử lý lỗi, **When** nhà tuyển dụng chọn "Thử lại mục lỗi", **Then** chỉ các mục lỗi được xử lý lại và kết quả thành công trước đó được giữ nguyên.

---

### User Story 3 - Đánh giá ứng viên có bằng chứng (Priority: P1)

Là nhà tuyển dụng, tôi muốn xem tóm tắt hồ sơ, dữ liệu đã trích xuất, tiêu chí đạt/chưa đạt và bằng chứng từ CV cho từng nhận định AI, để có thể kiểm chứng thay vì dựa vào một điểm số đơn lẻ.

**Why this priority**: AI chỉ nên hỗ trợ quyết định. Bằng chứng và CV gốc là điều kiện để nhà tuyển dụng chịu trách nhiệm cho quyết định cuối cùng.

**Independent Test**: Mở một hồ sơ đã phân tích và kiểm tra rằng mỗi kỹ năng/kinh nghiệm quan trọng đều dẫn đến đoạn bằng chứng, CV gốc có thể xem, dữ liệu trích xuất có mức tin cậy và kết quả chính thức ghi nhận phiên bản tiêu chí.

**Acceptance Scenarios**:

1. **Given** một kết luận AI về kỹ năng hoặc kinh nghiệm, **When** nhà tuyển dụng mở chi tiết, **Then** hệ thống hiển thị đoạn CV liên quan hoặc ghi rõ không tìm thấy bằng chứng trực tiếp.
2. **Given** trường dữ liệu được trích xuất với độ tin cậy thấp, **When** hiển thị trong hồ sơ, **Then** trường đó được đánh dấu để kiểm tra thủ công và không được trình bày như sự thật chắc chắn.
3. **Given** nhà tuyển dụng cần kiểm chứng hồ sơ, **When** chọn xem CV gốc, **Then** tài liệu mở đúng ứng viên mà không làm mất ngữ cảnh đánh giá hiện tại.

---

### User Story 4 - Sàng lọc và thao tác hàng loạt (Priority: P2)

Là nhà tuyển dụng xử lý nhiều hồ sơ, tôi muốn tìm kiếm, sắp xếp, lọc, chọn nhiều ứng viên và thực hiện hành động hàng loạt, để giảm số lần mở từng hồ sơ.

**Why this priority**: Sau khi kết quả đáng tin cậy, hiệu suất thao tác quyết định mức độ sử dụng thường xuyên.

**Independent Test**: Trên danh sách 500 ứng viên, áp dụng bộ lọc tiêu chí bắt buộc, kỹ năng, điểm và trạng thái; chọn 20 ứng viên trên nhiều trang rồi chuyển trạng thái, gắn tag và xuất dữ liệu.

**Acceptance Scenarios**:

1. **Given** danh sách đã sàng lọc, **When** nhà tuyển dụng kết hợp nhiều bộ lọc và sắp xếp, **Then** kết quả, số lượng và trạng thái bộ lọc được cập nhật rõ ràng.
2. **Given** nhiều ứng viên được chọn qua nhiều trang, **When** thực hiện một hành động hàng loạt, **Then** hệ thống xác nhận phạm vi và báo kết quả thành công/thất bại theo từng hồ sơ.
3. **Given** nhà tuyển dụng đã tùy chỉnh cột và bộ lọc, **When** quay lại vị trí đó, **Then** bố cục làm việc được khôi phục.

---

### User Story 5 - Quản lý pipeline và lý do quyết định (Priority: P2)

Là thành viên nhóm tuyển dụng, tôi muốn chuyển ứng viên qua các giai đoạn tuyển dụng, thêm ghi chú và ghi nhận lý do chọn/loại, để quyết định có ngữ cảnh và có thể truy vết.

**Why this priority**: Điểm AI không thay thế quy trình tuyển dụng. Pipeline và nhật ký quyết định giúp hệ thống trở thành workspace thay vì chỉ là báo cáo.

**Independent Test**: Chuyển một ứng viên từ Mới nhận đến Phỏng vấn chuyên môn, thêm ghi chú, sau đó từ chối với lý do; xác nhận timeline lưu đủ người thực hiện, thời gian và nội dung thay đổi.

**Acceptance Scenarios**:

1. **Given** một ứng viên đang ở một giai đoạn, **When** trạng thái thay đổi, **Then** timeline ghi nhận trạng thái cũ, trạng thái mới, thời gian và người thực hiện.
2. **Given** ứng viên bị từ chối, **When** hoàn tất quyết định, **Then** hệ thống yêu cầu chọn lý do và cho phép ghi chú bổ sung.
3. **Given** AI đề xuất một kết quả nhưng nhà tuyển dụng quyết định khác, **When** lưu quyết định, **Then** hệ thống giữ cả đề xuất AI và quyết định con người, không ghi đè lịch sử.

---

### User Story 6 - So sánh ứng viên cuối vòng (Priority: P2)

Là hiring manager, tôi muốn so sánh từ hai đến năm ứng viên theo cùng bộ tiêu chí và bằng chứng, để chọn người phù hợp mà không phải ghi nhớ thông tin từ nhiều modal.

**Why this priority**: So sánh trực tiếp hỗ trợ giai đoạn ra quyết định sau shortlist.

**Independent Test**: Chọn ba ứng viên và mở chế độ so sánh; xác nhận các tiêu chí, kinh nghiệm, cảnh báo bắt buộc, điểm AI, bằng chứng và ghi chú hiển thị trên cùng một ma trận.

**Acceptance Scenarios**:

1. **Given** từ hai đến năm ứng viên được chọn, **When** mở so sánh, **Then** mọi ứng viên được đánh giá theo cùng phiên bản tiêu chí.
2. **Given** dữ liệu của một ứng viên còn thiếu hoặc độ tin cậy thấp, **When** so sánh, **Then** ô tương ứng thể hiện "Chưa đủ dữ liệu" thay vì mặc định là không đạt.

---

### User Story 7 - Theo dõi hiệu quả và cộng tác cơ bản (Priority: P3)

Là trưởng nhóm tuyển dụng, tôi muốn biết số hồ sơ ở từng giai đoạn, thời gian xử lý, tỷ lệ lỗi và tỷ lệ recruiter điều chỉnh đề xuất AI, để phát hiện nút thắt và đánh giá chất lượng quy trình.

**Why this priority**: Báo cáo có giá trị sau khi dữ liệu quyết định và pipeline đã ổn định.

**Independent Test**: Tạo dữ liệu tuyển dụng qua nhiều giai đoạn và xác nhận dashboard tổng hợp đúng số lượng, thời gian và tỷ lệ override theo vị trí.

**Acceptance Scenarios**:

1. **Given** một vị trí có lịch sử xử lý, **When** trưởng nhóm mở tổng quan, **Then** thấy funnel theo giai đoạn, số CV lỗi/trùng và thời gian xử lý trung vị.
2. **Given** quyết định con người khác đề xuất AI, **When** xem báo cáo chất lượng, **Then** trường hợp được tính vào tỷ lệ override nhưng không tự động làm thay đổi mô hình.

### Edge Cases

- Tổng trọng số bị thay đổi đồng thời ở hai phiên làm việc hoặc cấu hình bị cập nhật trong khi một lô đang chạy.
- CV có điểm cao nhưng thiếu tiêu chí bắt buộc; CV không đủ dữ liệu để xác định tiêu chí bắt buộc.
- Tệp PDF đặt mật khẩu, hỏng, chỉ chứa ảnh, không có thông tin liên hệ hoặc sử dụng tiếng Việt xen tiếng Anh.
- Một CV được nộp nhiều lần cho cùng vị trí hoặc cho nhiều vị trí khác nhau.
- Lô xử lý bị mất kết nối, tải lại trang, dừng giữa chừng hoặc một số tác vụ AI hết thời gian chờ.
- Nhà tuyển dụng chọn ứng viên trên nhiều trang rồi thay đổi bộ lọc.
- Ứng viên đã được cập nhật pipeline trong lúc một người khác đang xem hoặc thao tác hàng loạt.
- Dữ liệu trích xuất mâu thuẫn với CV gốc hoặc không có bằng chứng đủ mạnh.
- Phiên bản JD/trọng số thay đổi sau khi đã có shortlist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Hệ thống MUST cho phép phân loại tiêu chí tuyển dụng thành bắt buộc, ưu tiên và cộng điểm.
- **FR-002**: Hệ thống MUST hỗ trợ tiêu chí loại trực tiếp và hiển thị rõ lý do ứng viên bị gắn cờ.
- **FR-003**: Tổng trọng số chấm điểm MUST bằng 100% trước khi có thể lưu làm cấu hình chính thức.
- **FR-004**: Hệ thống MUST lưu phiên bản tiêu chí và gắn mỗi kết quả sàng lọc với đúng phiên bản đã sử dụng.
- **FR-005**: Hệ thống MUST phân biệt trực quan giữa điểm chính thức và điểm mô phỏng khi trọng số chưa được lưu hoặc chưa chạy lại.
- **FR-006**: Khi cấu hình chính thức thay đổi, hệ thống MUST cho biết kết quả nào đã cũ và cho phép chạy lại có chủ đích.
- **FR-007**: Hệ thống MUST tiếp nhận lô tối thiểu 200 CV và theo dõi trạng thái ở cấp lô lẫn cấp tệp.
- **FR-008**: Lỗi xử lý một CV MUST NOT làm dừng các CV còn lại trong lô.
- **FR-009**: Nhà tuyển dụng MUST có thể thử lại riêng các CV lỗi hoặc hủy các mục chưa bắt đầu.
- **FR-010**: Hệ thống MUST phát hiện khả năng trùng lặp theo tệp, nội dung và thông tin liên hệ; quyết định giữ, thay thế hoặc bỏ qua thuộc về người dùng.
- **FR-011**: Hệ thống MUST lưu trạng thái xử lý, thông báo lỗi dễ hiểu và chi tiết kỹ thuật đủ để hỗ trợ điều tra.
- **FR-012**: Hồ sơ ứng viên MUST hiển thị tóm tắt, thông tin liên hệ, vị trí hiện tại, tổng kinh nghiệm liên quan, công ty gần nhất, học vấn và kỹ năng nổi bật khi dữ liệu có sẵn.
- **FR-013**: Mỗi kết luận AI quan trọng MUST kèm bằng chứng trích từ CV hoặc trạng thái "Không tìm thấy bằng chứng trực tiếp".
- **FR-014**: Dữ liệu trích xuất MUST có chỉ báo độ tin cậy và đánh dấu các trường cần kiểm tra thủ công.
- **FR-015**: Nhà tuyển dụng MUST có thể xem CV gốc từ hồ sơ chi tiết mà không mất trạng thái danh sách hiện tại.
- **FR-016**: Hệ thống MUST hiển thị ma trận tiêu chí đạt, chưa đạt, chưa đủ dữ liệu và không áp dụng.
- **FR-017**: Danh sách ứng viên MUST hỗ trợ tìm kiếm, nhiều bộ lọc đồng thời và sắp xếp theo điểm, ngày nhận, kinh nghiệm, trạng thái và mức độ rủi ro.
- **FR-018**: Nhà tuyển dụng MUST có thể tùy chọn cột và lưu chế độ xem theo từng vị trí.
- **FR-019**: Nhà tuyển dụng MUST có thể chọn ứng viên trên nhiều trang và biết chính xác phạm vi đang được chọn.
- **FR-020**: Hệ thống MUST hỗ trợ thao tác hàng loạt: chuyển trạng thái, gắn tag, xuất dữ liệu và chạy lại phân tích.
- **FR-021**: Mỗi thao tác hàng loạt MUST có bước xác nhận phạm vi và báo kết quả ở cấp hồ sơ.
- **FR-022**: Pipeline mặc định MUST gồm: Mới nhận, AI đã phân tích, Recruiter đang xem, Shortlist, Phỏng vấn HR, Phỏng vấn chuyên môn, Đề nghị tuyển dụng, Đã tuyển và Từ chối.
- **FR-023**: Hệ thống MUST cho phép lưu ghi chú nội bộ và lý do quyết định; từ chối ứng viên MUST có lý do.
- **FR-024**: Hệ thống MUST lưu lịch sử trạng thái, ghi chú, thay đổi tiêu chí và quyết định override với người thực hiện và thời gian.
- **FR-025**: Quyết định của con người MUST được lưu riêng với đề xuất AI và không làm thay đổi kết quả AI gốc.
- **FR-026**: Người dùng MUST có thể so sánh từ hai đến năm ứng viên theo cùng phiên bản tiêu chí.
- **FR-027**: Chế độ so sánh MUST hiển thị điểm, tiêu chí bắt buộc, kinh nghiệm, kỹ năng, bằng chứng, cảnh báo dữ liệu và ghi chú quyết định.
- **FR-028**: Dashboard MUST tổng hợp funnel pipeline, số CV hợp lệ/lỗi/trùng, thời gian xử lý và tỷ lệ override theo vị trí.
- **FR-029**: Hệ thống MUST giữ trạng thái lô và cho phép người dùng tiếp tục theo dõi sau khi tải lại trang.
- **FR-030**: Mọi hành động có thể thay đổi quyết định tuyển dụng MUST có phản hồi thành công/thất bại rõ ràng và không được báo thành công khi chỉ một phần hoàn tất.
- **FR-031**: Hệ thống MUST hạn chế hiển thị dữ liệu cá nhân theo quyền truy cập hiện có và ghi lại việc tải/xuất dữ liệu ứng viên.
- **FR-032**: Hệ thống MUST hỗ trợ xóa hoặc ẩn danh hồ sơ theo chính sách lưu trữ được cấu hình, đồng thời giữ log nghiệp vụ không chứa dữ liệu cá nhân quá mức cần thiết.

### Key Entities

- **Screening Criteria Set**: Phiên bản tiêu chí của một vị trí, gồm loại tiêu chí, trọng số, điều kiện đạt và trạng thái hiệu lực.
- **Criterion**: Một yêu cầu cụ thể có loại bắt buộc/ưu tiên/cộng điểm, toán tử đánh giá, giá trị kỳ vọng và mức độ quan trọng.
- **Upload Batch**: Một phiên tải nhiều CV, gồm người tạo, vị trí, tiến độ, tổng số tệp, số thành công/lỗi/trùng và trạng thái phục hồi.
- **Resume Processing Item**: Trạng thái của từng CV trong lô, lỗi, số lần thử lại, dấu vết trùng lặp và liên kết hồ sơ ứng viên.
- **Candidate Profile**: Dữ liệu ứng viên đã chuẩn hóa cùng các trường trích xuất, độ tin cậy và CV gốc.
- **Evidence Snippet**: Đoạn bằng chứng từ CV hỗ trợ hoặc phản bác một tiêu chí/nhận định, gồm vị trí nguồn và mức tin cậy.
- **Screening Evaluation**: Kết quả chính thức của một ứng viên theo một phiên bản tiêu chí, gồm điểm thành phần, kết quả tiêu chí, cảnh báo và giải thích.
- **Recruitment Decision**: Quyết định của con người, trạng thái pipeline, lý do, ghi chú và quan hệ với đề xuất AI.
- **Candidate Tag**: Nhãn nghiệp vụ dùng để phân nhóm và thao tác hàng loạt.
- **Saved View**: Cấu hình cột, bộ lọc và sắp xếp của người dùng theo vị trí tuyển dụng.
- **Audit Event**: Sự kiện truy vết cho thay đổi tiêu chí, xử lý lô, trạng thái, ghi chú, override và xuất dữ liệu.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Nhà tuyển dụng có thể cấu hình và xác nhận bộ tiêu chí hợp lệ cho một vị trí trong dưới 5 phút mà không cần hướng dẫn ngoài hệ thống.
- **SC-002**: 100% kết quả chính thức truy ngược được về đúng phiên bản tiêu chí và bằng chứng đầu vào đã sử dụng.
- **SC-003**: Một lô 200 CV có thể tiếp tục xử lý khi có tệp lỗi; 100% lỗi được báo ở cấp tệp và có hành động khắc phục rõ ràng.
- **SC-004**: Nhà tuyển dụng có thể xác định 20 hồ sơ cần xem đầu tiên từ danh sách 500 ứng viên trong dưới 3 phút.
- **SC-005**: Ít nhất 90% kết luận kỹ năng/kinh nghiệm quan trọng hiển thị được bằng chứng CV hoặc trạng thái thiếu bằng chứng rõ ràng.
- **SC-006**: Nhà tuyển dụng có thể chuyển trạng thái và gắn tag cho 50 ứng viên trong một thao tác hoàn thành dưới 30 giây, không cần mở từng hồ sơ.
- **SC-007**: 100% quyết định từ chối, override và thay đổi pipeline có thể truy vết người thực hiện, thời gian và lý do.
- **SC-008**: Người dùng có thể so sánh ba ứng viên shortlist và xác định khác biệt chính trong dưới 2 phút.
- **SC-009**: Các thao tác lọc, sắp xếp và chuyển trang phản hồi trong dưới 1 giây với 1.000 hồ sơ trong điều kiện sử dụng tiêu chuẩn.
- **SC-010**: Trong kiểm thử khả dụng, ít nhất 85% recruiter hoàn thành luồng tải lô → sàng lọc → shortlist ngay lần đầu mà không cần hỗ trợ.
- **SC-011**: Tỷ lệ người dùng hiểu sai điểm mô phỏng là kết quả chính thức bằng 0 trong bộ kiểm thử nghiệm thu.

## Assumptions

- Giai đoạn đầu phục vụ recruiter và hiring manager trong cùng một tổ chức; quyền chi tiết có thể mở rộng sau nhưng mọi sự kiện vẫn cần định danh người thực hiện.
- PDF tiếp tục là định dạng CV chính; OCR cho PDF ảnh được xem là đường xử lý bổ sung, không làm giảm độ ổn định của PDF có text.
- AI đưa ra đề xuất, không tự động từ chối hoặc tuyển ứng viên nếu chưa có hành động xác nhận của con người.
- Điểm mô phỏng chỉ hỗ trợ khám phá; điểm chính thức luôn gắn với cấu hình đã lưu và lần chạy có thể truy vết.
- Phát hiện trùng lặp tạo cảnh báo, không tự động xóa hồ sơ.
- Pipeline mặc định có thể cấu hình ở giai đoạn sau; bản nâng cấp này ưu tiên một pipeline chuẩn dùng được ngay.
- Cơ chế xác thực hiện có được tái sử dụng; nếu chưa có danh tính người dùng, môi trường phát triển dùng một actor hệ thống rõ ràng thay vì bỏ trống audit.
- Chính sách lưu trữ mặc định tuân theo thực hành bảo vệ dữ liệu tuyển dụng và phải cấu hình được trước khi triển khai production.
- Tự động học lại mô hình từ feedback recruiter nằm ngoài phạm vi; dữ liệu override chỉ phục vụ audit và đánh giá chất lượng.
- Gửi email, đặt lịch phỏng vấn, kết nối ATS bên thứ ba và ứng viên tự cập nhật hồ sơ nằm ngoài phạm vi feature này.
