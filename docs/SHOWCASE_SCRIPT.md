# Kịch bản thuyết trình toàn bộ dự án Resume Screening AI

> **Cue release 1.1:** Trước khi bắt đầu, xác nhận badge hiển thị đúng `Offline · deterministic-keyword-v1` cho phương án dự phòng hoặc tên model online thực tế. Không gọi fallback là Gemini. Chỉ đọc metric từ báo cáo gắn với commit release cuối.

> **Cue Blind Review:** Bật “Đánh giá ẩn danh”, chỉ ra pseudonym và evidence đã che. Khi mở CV gốc, nói rõ đây là thao tác reveal chủ động có audit.

> **Nếu mạng/crawler/model lỗi:** Giữ `OFFLINE_MODE=true`, dùng job feed cục bộ và tiếp tục kịch bản. Video là phương án cuối sau live offline.

## 1. Cách kể đúng về sản phẩm

Resume Screening AI không chỉ là một màn hình sàng lọc CV. Đây là một nền tảng AI hai chiều cho thị trường tuyển dụng:

```text
Doanh nghiệp có JD                         Ứng viên có CV
        │                                      │
        ├── tìm đúng người      tìm đúng việc ─┤
        │                                      │
        └────────── AI Matching Core ──────────┘
                     │
          Điểm + bằng chứng + khoảng trống
                     │
             Con người ra quyết định
```

Câu chuyện thuyết trình phải đi qua cả hai phía:

- Nhà tuyển dụng: tạo yêu cầu, xử lý nhiều CV, đánh giá và ra quyết định.
- Người tìm việc: khám phá việc làm thật và nhận lộ trình cải thiện CV.

Không trình bày theo menu và không đọc danh sách tính năng. Mỗi phân hệ phải trả lời một câu hỏi thực tế trong cùng một hành trình.

## 2. Thông điệp trung tâm

> Resume Screening AI là cầu nối thông minh giữa yêu cầu của doanh nghiệp và năng lực của ứng viên: giúp doanh nghiệp tìm đúng người, giúp ứng viên tìm đúng việc, đồng thời giải thích rõ vì sao hai phía phù hợp hoặc còn thiếu điều gì.

Ba điều khán giả cần nhớ:

1. Một AI matching core được tái sử dụng cho cả recruiter và ứng viên.
2. AI không chỉ cho điểm mà còn đưa ra thành phần điểm, bằng chứng, điểm mạnh và khoảng trống.
3. Hệ thống hoạt động như công cụ hỗ trợ quyết định, có fallback và có thể tái tạo từ mã nguồn mở.

## 3. Tỷ trọng bài trình bày

Trong 7 phút:

- 15% bài toán và tầm nhìn toàn dự án.
- 50% live demo bốn phân hệ.
- 15% cơ chế AI và kiến trúc.
- 10% độ ổn định, mã nguồn mở và khả năng tái tạo.
- 10% kết quả, tác động và kết luận.

Cơ chế hoạt động cần được trình bày, nhưng chỉ sau khi khán giả đã thấy giá trị. Công thức cho mỗi đoạn demo là:

> Người dùng cần gì → sản phẩm làm gì → kết quả có ý nghĩa gì → một câu giải thích cơ chế.

## 4. Bốn khoảnh khắc nổi bật của toàn dự án

### Khoảnh khắc 1 - Từ hàng trăm CV đến shortlist có kiểm soát

Upload một batch gồm CV tốt, CV thiếu dữ liệu, file trùng và file lỗi. Bảng xếp hạng vẫn hình thành; lỗi một file không làm dừng cả lô.

**Giá trị**: tự động hóa công việc lặp lại của recruiter mà không mất khả năng kiểm soát.

### Khoảnh khắc 2 - Từ điểm số về đúng CV gốc

Mở Candidate Detail, xem điểm Skills/Experience/Education, strengths/gaps và bấm vào evidence để kiểm tra trong CV. Một yêu cầu không có bằng chứng phải là `UNKNOWN`, không tự động là không đạt.

**Giá trị**: biến AI từ “hộp đen cho điểm” thành trợ lý có thể kiểm chứng.

### Khoảnh khắc 3 - Một CV tự tìm ra việc phù hợp

Tải cùng CV lên Real Jobs Portal. AI nhận diện nhóm nghề, xếp lại công việc từ TopCV/ITViec theo tỷ lệ phù hợp và giải thích điểm mạnh/khoảng trống trước khi ứng tuyển.

**Giá trị**: đảo chiều bài toán matching để phục vụ người tìm việc.

### Khoảnh khắc 4 - Khoảng trống trở thành lộ trình

Đưa CV và JD mục tiêu vào Career Gap Advisor. Hệ thống không dừng ở “chưa phù hợp” mà chỉ ra kỹ năng đã có, kỹ năng thiếu và các bước ưu tiên tiếp theo.

**Giá trị**: chuyển kết quả matching thành hành động phát triển nghề nghiệp.

## 5. Kịch bản sân khấu 7 phút

### 0:00-0:40 - Hook: cùng một khoảng cách, hai phía đều gặp khó

**Màn hình**: Slide mở đầu với hai cột “Doanh nghiệp: quá nhiều CV” và “Ứng viên: quá nhiều việc làm”. Ở giữa là chữ “Mismatch”.

**Lời thoại**:

“Thị trường tuyển dụng đang có một nghịch lý. Doanh nghiệp nhận hàng trăm CV nhưng vẫn khó tìm đúng người. Ứng viên nhìn thấy hàng nghìn tin tuyển dụng nhưng vẫn không biết công việc nào thực sự phù hợp với mình.”

“Hai vấn đề này thực chất là cùng một bài toán: khoảng cách giữa yêu cầu công việc và năng lực được thể hiện trong CV.”

“Resume Screening AI sử dụng một lõi matching chung để giải quyết khoảng cách đó cho cả hai phía.”

### 0:40-1:05 - Bản đồ toàn bộ sản phẩm

**Màn hình**: Slide một dòng gồm bốn phân hệ.

```text
Recruiter Workspace → Candidate Intelligence → Real Jobs → Career Gap Advisor
```

**Lời thoại**:

“Sản phẩm có bốn phân hệ liên kết. Nhà tuyển dụng tổ chức một đợt sàng lọc; Candidate Intelligence giải thích từng hồ sơ; Real Jobs giúp ứng viên tìm cơ hội phù hợp; Career Gap Advisor biến phần còn thiếu thành lộ trình cải thiện.”

“Sau đây tôi sẽ dùng một JD và một nhóm CV xuyên suốt để cho thấy dữ liệu di chuyển qua toàn hệ thống như thế nào.”

### 1:05-2:20 - Phân hệ 1: Recruiter Workspace

**Màn hình**: Không gian tuyển dụng với JD demo và batch CV đã chuẩn bị.

**Thao tác**:

1. Chọn hoặc tạo JD “Software Engineer”.
2. Chỉ vào trọng số Skills/Experience/Education và tiêu chí bắt buộc.
3. Upload 8-10 CV synthetic cùng lúc.
4. Cho thấy progress từng file, duplicate, file lỗi và ranking/filter.

**Lời thoại**:

“Đầu tiên, recruiter mô tả vị trí và xác định điều gì quan trọng. Trọng số cho phép điều chỉnh theo từng vai trò, còn tiêu chí bắt buộc được đánh giá riêng để một điểm trung bình cao không che khuất yêu cầu quan trọng.”

“Thay vì tải từng hồ sơ, recruiter có thể đưa cả batch vào hệ thống. Mỗi file có trạng thái riêng: hợp lệ, đang phân tích, trùng, cần kiểm tra hoặc lỗi. Một PDF hỏng không làm mất kết quả của các CV còn lại.”

“Kết quả được xếp hạng, tìm kiếm, lọc theo điểm/trạng thái/khoảng trống và có thể đưa qua các bước xử lý tuyển dụng.”

**Cơ chế một câu**: “Mỗi lần chấm gắn với đúng JD, trọng số và phiên bản tiêu chí đã sử dụng nên kết quả có thể truy vết.”

### 2:20-3:20 - Phân hệ 2: Candidate Intelligence

**Màn hình**: Candidate Detail của một hồ sơ có điểm khá cao nhưng còn thiếu mandatory evidence.

**Thao tác**:

1. Mở hồ sơ từ bảng xếp hạng.
2. Chỉ breakdown Skills/Experience/Education.
3. Chỉ strengths, gaps và honors nếu fixture có.
4. Mở evidence trong CV và một criterion `UNKNOWN`.
5. Nếu final đã hoàn thiện, sửa một dữ liệu sai hoặc mở decision timeline.

**Lời thoại**:

“Một con số 82% chưa đủ để tuyển dụng. Vì vậy hồ sơ chi tiết phân rã điểm thành kỹ năng, kinh nghiệm và học vấn; đồng thời chỉ ra điểm mạnh, khoảng trống và thành tích nổi bật.”

“Quan trọng hơn, mỗi kết luận có thể dẫn về bằng chứng trong CV. Với kỹ năng này, hệ thống tìm thấy nguồn trực tiếp. Với yêu cầu kia, hệ thống không tìm thấy bằng chứng nên trả về ‘chưa đủ dữ liệu’, không tự quy kết ứng viên không đạt.”

“AI đưa ra recommendation; recruiter mới là người shortlist hoặc từ chối. Nếu con người quyết định khác AI, cả hai kết quả được giữ riêng trong lịch sử.”

**Câu nhấn**: “Chúng tôi tự động hóa việc đọc hồ sơ, không tự động hóa trách nhiệm tuyển dụng.”

### 3:20-4:20 - Phân hệ 3: Real Jobs Portal

**Màn hình**: Trang Khám phá việc làm với banner, danh sách việc làm và CV đã chọn sẵn.

**Thao tác**:

1. Cho thấy dữ liệu việc làm từ TopCV/ITViec hoặc curated fallback.
2. Upload một CV.
3. Bấm “Gợi ý việc phù hợp”.
4. Chỉ ngành nghề được nhận diện, match percentage và lý do.
5. Lọc theo địa điểm/ngành/điểm rồi mở link ứng tuyển.

**Lời thoại**:

“Bây giờ chúng ta chuyển sang phía ứng viên. Thay vì nhập hàng loạt từ khóa, người dùng chỉ cần tải CV. Hệ thống nhận diện nhóm chuyên môn rồi xếp lại các công việc thực tế theo mức phù hợp cá nhân.”

“Mỗi kết quả không chỉ có tỷ lệ match. Ứng viên biết mình phù hợp ở kỹ năng nào, còn thiếu điều gì, mức kinh nghiệm ra sao và có thể đi tới nguồn tuyển dụng gốc.”

“Nếu website nguồn thay đổi hoặc mất mạng, curated feed giữ hành trình demo hoạt động và hệ thống thể hiện rõ đang dùng fallback.”

**Cơ chế một câu**: “Cùng biểu diễn CV/JD và scoring core ở phía recruiter được đảo chiều để xếp hạng nhiều việc làm cho một ứng viên.”

### 4:20-5:05 - Phân hệ 4: Career Gap Advisor

**Màn hình**: Cố vấn nghề nghiệp với cùng CV và một JD mục tiêu cao hơn.

**Thao tác**:

1. Dán JD mục tiêu.
2. Chọn CV đã chuẩn bị.
3. Chạy phân tích.
4. Chỉ matched skills, missing skills và roadmap.

**Lời thoại**:

“Nếu ứng viên chưa phù hợp thì sao? Một hệ thống tốt không nên chỉ trả về ‘không đạt’.”

“Career Gap Advisor so sánh CV với vị trí mục tiêu, tách rõ năng lực hiện có và khoảng trống, sau đó ưu tiên các bước cải thiện. Kết quả matching vì vậy trở thành một lộ trình hành động chứ không phải một bản án.”

“Đây là vòng khép kín của sản phẩm: doanh nghiệp hiểu ứng viên, ứng viên hiểu thị trường và hiểu mình cần phát triển điều gì.”

### 5:05-5:50 - Cơ chế AI chung của toàn hệ thống

**Màn hình**: Một slide kiến trúc đơn giản, không mở source code.

```text
CV/JD/PDF
   ↓
Trích xuất và chuẩn hóa dữ liệu
   ↓
Semantic matching + scoring theo thành phần
   ↓
Gemini reasoning/reranking (tùy chọn)
   ↓
Evidence, strengths, gaps và recommendation
   ↓
Recruiter hoặc ứng viên hành động
```

**Lời thoại**:

“Bốn phân hệ không phải bốn demo rời rạc. Chúng dùng chung một pipeline.”

“PDF được trích xuất và chuẩn hóa. Embedding đo tương đồng ngữ nghĩa thay vì chỉ đếm từ khóa. Scoring phân tích kỹ năng, kinh nghiệm và học vấn. Gemini có thể bổ sung reasoning/reranking, nhưng không phải dependency bắt buộc.”

“Lớp cuối cùng chuyển kết quả thành evidence cho recruiter, job recommendation cho ứng viên hoặc skill roadmap cho định hướng nghề nghiệp.”

**Không nói**: chi tiết class, database table, endpoint hoặc công thức dài trừ khi giám khảo hỏi.

### 5:50-6:20 - Độ ổn định, Responsible AI và mã nguồn mở

**Màn hình**: Slide ba cột “Reliable - Responsible - Open”.

**Lời thoại**:

“Hệ thống có local fallback khi Gemini, model hoặc crawler không khả dụng; batch chịu lỗi theo từng file; test tự động bao phủ backend, component và hành trình trình duyệt.”

“AI không auto-reject. Thiếu bằng chứng là UNKNOWN. Dữ liệu demo là synthetic/ẩn danh, và hệ thống hỗ trợ audit, quyền truy cập và anonymization.”

“Dự án phát hành theo MIT, mã nguồn có SPDX, dependency/license được kiểm kê và release có thể build lại từ source.”

### 6:20-6:40 - Kết quả đo được

**Màn hình**: Slide metric final.

**Lời thoại mẫu**:

“Trên bộ [N] CV synthetic/ẩn danh và [M] JD, phiên bản [dataset], hệ thống đạt mandatory recall [x], evidence precision [y], UNKNOWN accuracy [z] và ranking agreement [r]. Toàn bộ report gắn với release SHA và cấu hình AI cụ thể.”

**Quy tắc**:

- Chỉ thay placeholder bằng kết quả benchmark final.
- Luôn hiển thị sample size và mode online/offline.
- Không dùng target hoặc số test tự động thay cho chất lượng AI thực đo.

### 6:40-7:00 - Kết luận toàn dự án

**Màn hình**: Hai phía thị trường được nối bằng Resume Screening AI.

**Lời thoại**:

“Resume Screening AI không chỉ giúp đọc CV nhanh hơn. Sản phẩm tạo một ngôn ngữ chung giữa điều doanh nghiệp cần và điều ứng viên có.”

“Doanh nghiệp tìm đúng người bằng kết quả có thể kiểm chứng. Ứng viên tìm đúng việc và biết bước tiếp theo để tiến gần hơn tới công việc mình muốn.”

“Tìm đúng người. Tìm đúng việc. Và luôn hiểu vì sao.”

## 6. Cấu trúc slide tối đa 8 trang

1. **The mismatch**: doanh nghiệp quá nhiều CV, ứng viên quá nhiều lựa chọn.
2. **One core, two journeys**: sơ đồ hai phía và bốn phân hệ.
3. **Recruiter flow**: JD → batch → ranking → decision.
4. **Explainable candidate intelligence**: score breakdown + evidence + UNKNOWN.
5. **Candidate flow**: Real Jobs → Gap Advisor.
6. **Shared AI mechanism**: pipeline năm bước.
7. **Proof**: benchmark + reliability + open-source release.
8. **Closing**: “Tìm đúng người. Tìm đúng việc. Luôn hiểu vì sao.”

Slide 3-5 chỉ dùng ảnh hoặc sơ đồ đơn giản; phần chứng minh chính diễn ra trong live demo.

## 7. Dữ liệu demo xuyên suốt

Không dùng dữ liệu khác nhau cho từng phân hệ. Chuẩn bị một “demo universe” thống nhất:

- Một JD Software Engineer và một JD mục tiêu Senior AI Engineer.
- 8-10 CV synthetic, trong đó một CV được dùng xuyên suốt phía ứng viên.
- Một hồ sơ điểm cao nhưng thiếu mandatory.
- Một hồ sơ có evidence rõ ở trang 2/3 và một criterion `UNKNOWN`.
- Một file trùng, một PDF scan và một PDF hỏng.
- 15-20 job listing thuộc nhiều ngành, có ít nhất 3 kết quả phù hợp với CV chính.
- Gap Advisor phải cho ra 2-3 matched skills, 2-3 gaps và roadmap dễ hiểu.

Sự liên tục của dữ liệu giúp khán giả cảm thấy đây là một sản phẩm thống nhất thay vì bốn trang web ghép lại.

## 8. Những thứ nên khoe và không nên sa đà

### Nên khoe

- Bốn phân hệ dùng chung matching core.
- Batch CV chịu lỗi và phát hiện trùng.
- Scoring theo Skills/Experience/Education và mandatory gate.
- Candidate evidence, `UNKNOWN`, strengths/gaps và human decision.
- Nhận diện chuyên môn CV và rerank việc làm thật.
- Gap roadmap có hành động cụ thể.
- Online/offline fallback.
- Test, MIT/SPDX, tài liệu và release tái tạo được.

### Chỉ nói khi được hỏi

- Danh sách endpoint và database table.
- Chi tiết migration hoặc state enum.
- Tên mọi dependency.
- Tất cả filter/export/button phụ.
- Toàn bộ lịch sử refactor giao diện.

### Không tuyên bố

- “AI chính xác tuyệt đối”.
- “Không có bias”.
- “Thay thế recruiter”.
- “Production-ready” khi authentication, encryption và hạ tầng production chưa hoàn chỉnh.
- “Dữ liệu real-time” nếu đang sử dụng curated fallback.

## 9. Câu hỏi phản biện toàn dự án

### “Sản phẩm giải quyết một hay nhiều bài toán?”

“Một bài toán nền tảng là đo và giải thích khoảng cách CV-JD. Bốn phân hệ là bốn hành động khác nhau trên cùng kết quả: recruiter sàng lọc, kiểm chứng ứng viên, người tìm việc khám phá việc và xây lộ trình.”

### “Điểm khác biệt với ATS hoặc job portal thông thường?”

“ATS thường quản lý pipeline, job portal thường tìm bằng từ khóa. Sản phẩm kết nối hai phía bằng cùng AI core, đồng thời bổ sung criteria version, component score, evidence, UNKNOWN, strengths/gaps và human audit.”

### “Gemini có phải toàn bộ AI không?”

“Không. Trích xuất, semantic embedding, component scoring và rule/evidence vẫn hoạt động độc lập. Gemini là reasoning/reranking tùy chọn; report luôn ghi rõ mode.”

### “Dữ liệu TopCV/ITViec có thực sự trực tiếp không?”

“Hệ thống có connector để cập nhật metadata và link nguồn. Vì website ngoài có thể thay đổi hoặc giới hạn truy cập, demo có curated fallback và hiển thị rõ nguồn/mode; người dùng luôn đi tới tin gốc để ứng tuyển.”

### “Nếu CV thiếu thông tin thì sao?”

“Thiếu dữ liệu không đồng nghĩa không đạt. Hệ thống dùng UNKNOWN/manual review, hiển thị confidence và cho kiểm chứng trên CV gốc.”

### “Career Gap Advisor có bịa khóa học không?”

“Kết quả tập trung vào khoảng trống kỹ năng và thứ tự ưu tiên. Chỉ hiển thị tài nguyên cụ thể khi nguồn được kiểm chứng; không biến nội dung sinh tự động thành chứng chỉ hay cam kết việc làm.”

### “AI có ra quyết định tuyển dụng không?”

“Không. AI đưa ra recommendation và evidence; recruiter quyết định. Override và lý do được lưu riêng để audit.”

### “Tại sao đây là dự án mã nguồn mở có thể tin được?”

“Repository có lịch sử phát triển thực, giấy phép MIT/SPDX, dependency inventory, test/CI, build guide, AI documentation, benchmark và release được kiểm tra clean-room.”

## 10. Phương án dự phòng sân khấu

| Sự cố | Hành động | Câu chuyển |
|---|---|---|
| Gemini/Internet lỗi | Bật/open offline seed | “Đây là lúc fallback chứng minh hệ thống không phụ thuộc một dịch vụ.” |
| Crawler lỗi | Dùng curated job feed | “Nguồn ngoài không được phép làm hỏng trải nghiệm cốt lõi.” |
| Batch live chạy chậm | Mở batch pre-seeded | “Trạng thái được lưu theo từng CV; đây là batch đã hoàn tất từ cùng dataset.” |
| PDF viewer lỗi | Mở tab CV/screenshot evidence | “Evidence vẫn giữ trang và excerpt để người dùng kiểm chứng.” |
| Gap Advisor phản hồi chậm | Mở result đã chuẩn bị | “Kết quả này được tạo từ cùng CV và JD trong demo.” |
| Máy demo lỗi | Phát video offline | “Video sử dụng đúng release SHA và dataset được công bố.” |

Không sửa code, cài dependency hoặc nhập API key trên sân khấu.

## 11. Checklist diễn tập

- [ ] Bốn phân hệ đều xuất hiện và liên kết thành một câu chuyện.
- [ ] Không phân hệ nào chiếm quá 75 giây, trừ Recruiter + Candidate Detail cộng lại.
- [ ] Một CV được dùng xuyên suốt Recruiter, Real Jobs và Gap Advisor.
- [ ] Mỗi phân hệ có một câu “giá trị” và tối đa một câu “cơ chế”.
- [ ] Slide kiến trúc dưới 45 giây.
- [ ] Benchmark đã thay placeholder bằng số thực và sample size.
- [ ] Online/offline demo đều chạy được.
- [ ] Không có PII, API key, notification hoặc terminal history trên màn hình.
- [ ] Video dự phòng mở được không cần mạng.
- [ ] Hai lượt diễn tập liên tiếp hoàn tất trong 6:30-7:00.
- [ ] Người thuyết trình nhớ ba câu chuyển khi demo lỗi.
- [ ] Kết thúc bằng “Tìm đúng người. Tìm đúng việc. Và luôn hiểu vì sao.”
