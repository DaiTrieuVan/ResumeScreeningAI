# AI System Design and Evaluation

## 1. Vai trò của AI

AI hỗ trợ ba nhiệm vụ: biểu diễn ngữ nghĩa CV/JD, xếp hạng lại kèm giải thích và
tư vấn khoảng trống nghề nghiệp. AI không phải nguồn sự thật về năng lực và không
được tự động đưa ra quyết định tuyển dụng cuối cùng.

## 2. Pipeline

```text
PDF -> text normalization -> metadata/skills
   -> semantic retrieval -> rule/component scoring
   -> optional Gemini reranking and explanation
   -> evidence validation -> recruiter-facing result
```

### PDF và dữ liệu cấu trúc

`pdfplumber` trích xuất text từ PDF số. Regex xác định email/điện thoại và một số
metadata cơ bản. PDF ảnh hoặc file mã hóa có thể không đủ dữ liệu và phải được
đánh dấu để người dùng xử lý, không suy diễn nội dung.

### Semantic matching

Sentence Transformer tạo vector cho JD và CV; cosine similarity thu hẹp/xếp hạng
ứng viên. Model được lazy-load và có thể tắt bằng `DISABLE_EMBEDDING_MODEL=true`.
Khi model không khả dụng, hệ thống dùng keyword similarity xác định, giúp demo và
test không phụ thuộc download model.

### Gemini

Khi `GEMINI_API_KEY` tồn tại, Google GenAI SDK gọi model trong cấu hình
`DEFAULT_LLM_MODEL`. Prompt yêu cầu structured output và temperature thấp để giảm
dao động. Khi không có khóa hoặc request lỗi, các service chuyển sang rule/vector
fallback thay vì làm hỏng toàn workflow.

## 3. Scoring và criteria governance

- Criteria có loại `MANDATORY`, `PREFERRED`, `BONUS`.
- Tổng component weights phải bằng 100% trước khi publish.
- Official evaluation chỉ dùng criteria version đã publish.
- Slider chưa publish tạo simulation, không âm thầm đổi điểm chính thức.
- Mandatory gate độc lập với overall score.
- `UNKNOWN` dùng khi không có bằng chứng; `NOT_MET` chỉ dùng khi đủ căn cứ.

Mỗi evaluation lưu `criteria_set_id`, component scores, model information, input
fingerprint, evidence status và thời điểm đánh giá để hỗ trợ tái hiện.

## 4. Evidence và explainability

Mỗi criterion result có outcome, confidence, explanation và zero-or-more evidence
snippet gồm page/offset/excerpt. Giao diện đặt CV cạnh phân tích để recruiter kiểm
tra ngữ cảnh. Evidence không khớp hoặc không tồn tại phải hạ confidence và chuyển
sang manual review.

## 5. Evaluation plan

Trước release, dùng bộ CV tổng hợp/đã ẩn danh có ground truth do người đánh giá gán:

| Metric | Ý nghĩa | Mục tiêu ban đầu |
|---|---|---:|
| Mandatory recall | Tỷ lệ yêu cầu bắt buộc thật được phát hiện | >= 0.90 |
| Evidence precision | Tỷ lệ trích dẫn thực sự hỗ trợ kết luận | >= 0.90 |
| UNKNOWN accuracy | Không biến thiếu dữ liệu thành fail/pass | >= 0.95 |
| Ranking agreement | Spearman với thứ tự chuyên gia | >= 0.70 |
| Batch completion | File hợp lệ hoàn tất dù có file lỗi | >= 0.99 |
| Override rate | Quyết định người dùng khác AI | Theo dõi, không tối ưu mù quáng |

Ngưỡng là mục tiêu kỹ thuật, chưa phải kết quả đã được kiểm định. Báo cáo showcase
phải ghi sample size, dữ liệu, model/version và kết quả thực đo.

## 6. Bias và giới hạn

- CV viết dài hoặc dùng từ khóa giống JD có thể được ưu tiên ngoài ý muốn.
- Model embedding/LLM có thể phản ánh thiên lệch trong dữ liệu huấn luyện.
- Tên, tuổi, giới tính, ảnh, địa chỉ và trường học có thể trở thành proxy nhạy cảm.
- Kinh nghiệm không thể được chứng minh chỉ bằng câu chữ trong CV.
- Điểm giữa các job/criteria version khác nhau không nên so sánh trực tiếp.

Giảm thiểu bằng criteria minh bạch, evidence review, UNKNOWN, human decision,
audit/override analytics và dữ liệu test đa dạng. Không đưa thuộc tính được bảo vệ
vào scoring criteria.

## 7. Reproducibility checklist

Mỗi demo/báo cáo cần ghi:

- application release và commit SHA;
- model/provider/version;
- criteria version và weights;
- prompt/template version;
- input fingerprint hoặc dataset version;
- Gemini enabled/disabled;
- metric, sample size và ngày đo.

## 8. Failure behavior

- Gemini lỗi: dùng deterministic fallback và thông báo phù hợp.
- Embedding model lỗi: keyword similarity.
- Không trích xuất được text: item thất bại/needs review, không bịa dữ liệu.
- Live crawler lỗi: curated demo feed.
- Concurrent update: HTTP 409 để người dùng refresh/merge.
