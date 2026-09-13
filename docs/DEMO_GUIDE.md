# Competition Demo Guide

## Mục tiêu

Trong 5-7 phút, chứng minh ba ý: sản phẩm giải quyết vấn đề thật, AI có thể kiểm
chứng và hệ thống vẫn để con người chịu trách nhiệm quyết định.

## Chuẩn bị trước buổi thi

- Checkout đúng release tag và ghi commit SHA.
- Dùng laptop/adapter sẽ trình diễn; tắt update và notification gây gián đoạn.
- Khởi chạy backend/frontend trước, mở health check và tab dự phòng.
- Chuẩn bị một JD và 5-10 CV tổng hợp: phù hợp, thiếu mandatory, thiếu dữ liệu,
  duplicate và PDF lỗi.
- Warm-up embedding/browser nếu sử dụng; kiểm tra cả Gemini enabled và fallback.
- Không để API key, CV thật, email thật hoặc terminal history nhạy cảm trên màn hình.
- Quay video demo dự phòng và lưu offline.

## Kịch bản 6 phút

### 0:00-0:40 - Vấn đề

“Một recruiter nhận hàng trăm CV. Điểm AI đơn lẻ nhanh nhưng khó tin: không biết
tiêu chí nào, bằng chứng ở đâu và ai đã quyết định. Sản phẩm biến screening thành
quy trình có phiên bản, evidence và audit.”

### 0:40-1:30 - Criteria có quản trị

Mở Recruiter Workspace, chọn JD, giới thiệu mandatory/preferred/bonus. Cố publish
weights 95% để cho thấy validation, sau đó dùng criteria version hợp lệ.

### 1:30-2:20 - Batch bền vững

Upload bộ CV mẫu. Chỉ ra trạng thái từng file, duplicate và file lỗi; retry file
lỗi mà kết quả thành công không mất.

### 2:20-3:30 - AI có bằng chứng

Lọc/rank ứng viên, mở candidate drawer. Chỉ vào component score, mandatory gate,
`UNKNOWN`, confidence và evidence nằm cạnh CV. Nhấn mạnh hệ thống không bịa fail
khi thiếu dữ liệu.

### 3:30-4:30 - Con người ra quyết định

Chọn 2-3 finalist, mở comparison cùng criteria version. Shortlist một hồ sơ và
reject hồ sơ khác với reason; mở timeline cho thấy AI recommendation vẫn được giữ.

### 4:30-5:15 - Hai phía thị trường

Chuyển sang Real Jobs và Gap Advisor: CV người tìm việc được ghép việc thật và
nhận lộ trình kỹ năng, tái sử dụng cùng nền tảng matching.

### 5:15-6:00 - Kỹ thuật và tác động

Tóm tắt FastAPI/React, local embeddings + optional Gemini, fallback offline,
tests, privacy/anonymization và giấy phép MIT. Kết thúc bằng giá trị đo được:
thời gian triage, evidence precision và override analytics (chỉ dùng số đã đo).

## Câu hỏi phản biện dự kiến

**AI có tự động loại ứng viên không?** Không. Mandatory gate/score hỗ trợ ưu tiên;
decision là thao tác con người và được audit.

**Nếu AI không tìm thấy bằng chứng?** Kết quả là `UNKNOWN` và cần manual review,
không tự coi là fail.

**Điểm có thay đổi khi sửa slider?** Slider chưa publish chỉ là simulation. Điểm
official gắn với criteria version bất biến.

**Nếu Gemini hoặc Internet lỗi?** Rule/keyword/embedding fallback và curated job
feed giữ hành trình demo hoạt động.

**Dữ liệu CV được bảo vệ thế nào?** File nằm trong storage root, truy cập được audit,
có anonymization; production cần identity provider, TLS và encrypted storage.

**Làm sao biết model công bằng?** Không tuyên bố model công bằng tuyệt đối. Hệ thống
giảm rủi ro bằng criteria minh bạch, evidence, UNKNOWN, human override và kế hoạch
đánh giá bias/quality theo version.

## Phương án dự phòng

- Internet/Gemini mất: dùng `.env` offline và dữ liệu đã chuẩn bị.
- Live crawler đổi DOM: dùng curated feed và giải thích connector có fallback.
- Model chưa tải: đặt `DISABLE_EMBEDDING_MODEL=true`.
- Browser lỗi: video demo offline + API docs/screenshots.
- DB hỏng: dùng bản backup demo không chứa PII.
