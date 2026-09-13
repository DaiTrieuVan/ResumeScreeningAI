# Kịch bản thuyết trình Resume Screening AI

## Chiến lược trình bày

Không trình bày theo kiểu liệt kê tính năng và cũng không mở đầu bằng kiến trúc kỹ thuật. Cấu trúc thuyết phục nhất là:

```text
Nỗi đau thật -> Quyết định khó -> Demo giải pháp -> Bằng chứng cơ chế -> Kết quả đo -> Tác động
```

Tỷ trọng đề xuất cho 6 phút 30 giây:

- 55% câu chuyện nghiệp vụ và live demo.
- 25% cơ chế AI/kiến trúc để chứng minh độ tin cậy.
- 15% kết quả đo, mã nguồn mở và khả năng tái tạo.
- 5% kết luận và lời mời cộng đồng.

Nguyên tắc: mỗi chức năng chỉ xuất hiện khi nó trả lời một câu hỏi của recruiter. Sau mỗi thao tác, nói một câu về giá trị và tối đa một câu về cơ chế.

## Thông điệp trung tâm

> Resume Screening AI không thay recruiter bằng một con số. Hệ thống giúp họ xử lý hàng trăm CV nhanh hơn, nhưng mọi kết luận đều có tiêu chí, bằng chứng và quyết định cuối cùng vẫn thuộc về con người.

Ba điểm khán giả phải nhớ sau phần thi:

1. AI không bịa kết luận khi thiếu dữ liệu: hệ thống trả `UNKNOWN`.
2. Mọi nhận định quan trọng dẫn về bằng chứng trong CV và có thể được con người sửa/audit.
3. Hệ thống vẫn chạy khi mất Internet/Gemini và có thể build lại từ mã nguồn mở.

## Ba khoảnh khắc “wow” chính

### Wow 1 - Điểm cao chưa chắc phù hợp

Chọn một ứng viên có điểm tổng cao nhưng thiếu một yêu cầu bắt buộc. Hệ thống không tự shortlist; mandatory gate chuyển sang cần kiểm tra hoặc không đạt.

**Thông điệp**: “Một điểm trung bình đẹp không được phép che khuất điều kiện tuyển dụng quan trọng.”

### Wow 2 - Bấm vào kết luận, tới đúng bằng chứng

Từ criterion “Git” hoặc “2 năm kinh nghiệm”, bấm evidence để CV chuyển tới đúng trang/đoạn. Sau đó mở một criterion thiếu dữ liệu để thấy `UNKNOWN`, không phải `NOT_MET`.

**Thông điệp**: “AI phải chỉ ra nó đọc thấy điều gì, ở đâu và tự tin đến mức nào.”

### Wow 3 - Con người có quyền sửa và quyết định

Sửa một dữ liệu trích xuất sai hoặc override recommendation, nhập lý do rồi mở timeline. Kết quả AI gốc vẫn còn, quyết định con người được lưu riêng.

**Thông điệp**: “Chúng tôi tự động hóa việc đọc hồ sơ, không tự động hóa trách nhiệm.”

## Kịch bản mục tiêu 6 phút 30 giây

### 0:00-0:30 - Hook: 300 CV và một quyết định không thể giải thích

**Màn hình**: Slide mở đầu tối giản, chỉ có “300 CV - 1 vị trí - Bạn sẽ tin điểm AI nào?”

**Lời thoại**:

“Hãy tưởng tượng anh chị là recruiter và sáng nay nhận 300 CV cho một vị trí. Đọc thủ công thì mất nhiều ngày. Nhưng nếu AI chỉ trả về ‘82% phù hợp’, chúng ta vẫn chưa biết 82% dựa trên tiêu chí nào, bằng chứng ở đâu và liệu một yêu cầu bắt buộc có bị che khuất hay không.”

“Đó là lý do nhóm xây dựng Resume Screening AI: tăng tốc sàng lọc nhưng vẫn giữ được bằng chứng, khả năng kiểm tra và trách nhiệm của con người.”

**Không làm**: giới thiệu tên từng thành viên dài, đọc stack công nghệ hoặc kể lịch sử dự án.

### 0:30-1:05 - Đặt luật chơi trước khi AI chấm

**Màn hình**: Recruiter Workspace, một JD đã chuẩn bị; criteria mandatory/preferred và tổng trọng số.

**Thao tác**:

1. Chọn JD demo.
2. Chỉ vào mandatory/preferred.
3. Thử tổng trọng số 95% để validation xuất hiện, sau đó trở về cấu hình đã publish.

**Lời thoại**:

“AI không tự nghĩ ra thế nào là ứng viên tốt. Recruiter đặt luật chơi trước: đâu là bắt buộc, đâu là ưu tiên và trọng số nào được dùng. Mỗi bộ tiêu chí được lưu thành phiên bản; slider chưa publish chỉ là mô phỏng và không âm thầm đổi điểm chính thức.”

**Cơ chế một câu**: “Mỗi evaluation luôn gắn với một criteria version bất biến nên có thể tái hiện.”

### 1:05-1:50 - Upload batch chịu lỗi

**Màn hình**: Batch gồm 8-10 CV synthetic: hợp lệ, trùng, scan và PDF lỗi.

**Thao tác**:

1. Kéo thả cả lô.
2. Chỉ trạng thái từng file và progress tổng.
3. Xử lý một duplicate hoặc retry item lỗi.

**Lời thoại**:

“Trong thực tế, 300 CV không bao giờ sạch như nhau. Vì vậy lỗi một file không được làm dừng cả lô. Hệ thống theo dõi từng CV, phát hiện trùng ở nhiều lớp, giữ kết quả đã thành công và đưa file scan sang đường kiểm tra/OCR thay vì coi ứng viên là không đạt.”

**Cơ chế một câu**: “Mỗi item có state riêng, idempotency và recovery nên retry hoặc restart không tạo hồ sơ trùng.”

### 1:50-3:15 - Wow trung tâm: AI có bằng chứng

**Màn hình**: Bảng xếp hạng rồi Candidate Review Drawer chia đôi CV/kết quả.

**Thao tác**:

1. Mở ứng viên điểm cao nhưng mandatory gate chưa qua.
2. Bấm evidence “Git” để tới đúng trang CV.
3. Mở criterion “RESTful API” không có evidence và chỉ `UNKNOWN`.
4. Chỉ confidence và nguồn NATIVE/OCR/MANUAL.

**Lời thoại**:

“Ứng viên này đạt điểm tổng cao, nhưng hệ thống không tự shortlist vì còn một yêu cầu bắt buộc chưa đủ bằng chứng.”

“Với Git, AI không chỉ nói ‘đạt’. Chúng ta bấm vào đây và quay lại đúng đoạn CV mà hệ thống đã dùng. Còn với RESTful API, không tìm thấy bằng chứng không có nghĩa là ứng viên chắc chắn không biết. Kết quả đúng phải là ‘chưa đủ dữ liệu’ và cần recruiter xác minh.”

“Đây là khác biệt giữa một công cụ xếp hạng và một hệ thống hỗ trợ quyết định có thể kiểm chứng.”

**Cơ chế 20 giây**:

```text
PDF -> text theo trang -> semantic/rule matching
    -> criteria result -> evidence validation -> recruiter decision
```

“Embedding giúp tìm tương đồng ngữ nghĩa; rule kiểm tra tiêu chí; Gemini là lớp reasoning tùy chọn. Evidence validator không cho một kết luận thiếu nguồn trở thành sự thật chắc chắn.”

### 3:15-4:00 - Human-in-the-loop và audit

**Màn hình**: Correction/Decision Panel và timeline.

**Thao tác**:

1. Sửa một kỹ năng/số năm bị parser đọc sai, kèm lý do.
2. Cho thấy evaluation chuyển stale/cần chạy lại.
3. Shortlist hoặc reject một ứng viên với reason.
4. Mở timeline.

**Lời thoại**:

“AI có thể sai, nên recruiter phải sửa được dữ liệu. Khi sửa, hệ thống không âm thầm thay quá khứ: evaluation bị đánh dấu cần chạy lại, còn timeline lưu người sửa, thời gian và lý do.”

“Recommendation của AI và quyết định con người tồn tại song song. Đây là cách hệ thống tăng tốc mà không đẩy trách nhiệm sang thuật toán.”

### 4:00-4:35 - So sánh finalist và blind review

**Màn hình**: Comparison 3 ứng viên, bật Blind Review.

**Thao tác**:

1. So sánh 3 hồ sơ cùng criteria version.
2. Bật blind review để tên/email/file/evidence nhận diện được che.

**Lời thoại**:

“Ở vòng cuối, recruiter so sánh ứng viên trên cùng một bộ tiêu chí thay vì ghi nhớ nhiều cửa sổ. Với blind review, các trường nhận diện được che ở bảng, hồ sơ, so sánh và export để vòng đánh giá đầu tập trung vào bằng chứng nghề nghiệp.”

**Lưu ý**: Chỉ demo blind review khi privacy test matrix đã pass 100%.

### 4:35-5:05 - Hai phía của thị trường lao động

**Màn hình**: Real Jobs Portal và Career Gap Advisor; mỗi màn chỉ 10-12 giây.

**Lời thoại**:

“Cùng nền tảng matching này còn phục vụ người tìm việc: CV được ghép với tin tuyển dụng thực tế và chỉ ra khoảng trống so với JD mục tiêu. Vì vậy sản phẩm không chỉ giúp doanh nghiệp tìm đúng người, mà còn giúp ứng viên biết mình cần cải thiện điều gì.”

**Không làm**: cuộn danh sách việc làm dài hoặc giải thích crawler chi tiết.

### 5:05-5:40 - Chứng minh AI bằng số liệu

**Màn hình**: Một slide/report chỉ có 4 metric chính và cỡ mẫu.

**Lời thoại mẫu**:

“Chúng tôi không dùng target làm kết quả. Trên bộ [N] CV synthetic/ẩn danh, [M] JD, phiên bản [dataset], chế độ [offline/online], hệ thống đạt mandatory recall [x], evidence precision [y], UNKNOWN accuracy [z] và ranking agreement [r]. Báo cáo ghi đầy đủ model, criteria, prompt, release SHA và case lỗi.”

**Quy tắc bắt buộc**:

- Chỉ điền số từ benchmark final đã commit/release.
- Hiển thị sample size cạnh metric.
- Nếu metric chưa đạt, nói rõ giới hạn và cách manual review giảm rủi ro.
- Không dùng từ “chính xác tuyệt đối”, “không thiên lệch” hoặc “production-ready”.

### 5:40-6:10 - Mã nguồn mở và khả năng sống sót khi mất mạng

**Màn hình**: Slide kiến trúc + repository/release, không mở terminal dài.

**Lời thoại**:

“Sản phẩm được phát hành theo MIT, mỗi file code có SPDX, dependency và license được kiểm kê. Giám khảo có thể clone đúng release, build từ source và chạy lại benchmark.”

“Gemini, embedding model và crawler đều có fallback. Khi mất Internet, demo recruiter vẫn hoạt động bằng pipeline deterministic và dữ liệu curated; trạng thái fallback được hiển thị thay vì che giấu.”

### 6:10-6:30 - Kết thúc có câu nhớ

**Màn hình**: Logo + ba từ khóa “Nhanh hơn - Có bằng chứng - Con người quyết định”.

**Lời thoại**:

“Resume Screening AI không cố thay thế recruiter. Chúng tôi loại bỏ hàng giờ đọc lặp lại, nhưng giữ lại phần quan trọng nhất: tiêu chí minh bạch, bằng chứng kiểm chứng được và quyền quyết định của con người.”

“AI tuyển dụng đáng tin không phải AI luôn trả lời. Đó là AI biết khi nào mình chưa đủ dữ liệu.”

## Cấu trúc slide tối đa 7 trang

1. **Hook**: 300 CV - 1 vị trí - tin điểm AI nào?
2. **Luồng nghiệp vụ**: Criteria -> Batch -> Evidence -> Human decision.
3. **Điểm khác biệt**: evidence, UNKNOWN, versioning, audit.
4. **AI mechanism**: pipeline 5 bước, online/offline fallback.
5. **Measured results**: 4 metric + sample size + version.
6. **Open source/reproducibility**: MIT, CI, release, clean-room.
7. **Closing**: Nhanh hơn - Có bằng chứng - Con người quyết định.

Slide không lặp lại UI. Live demo là bằng chứng chính; slide chỉ giúp khán giả hiểu ý nghĩa.

## Dữ liệu demo cần chuẩn bị

- Một JD Software Engineer có 3 mandatory, 3 preferred và trọng số hợp lệ.
- 8-10 CV synthetic có tên rõ để thao tác nhưng không giống người thật.
- Một CV điểm cao nhưng thiếu mandatory.
- Một CV có evidence rõ ở trang 2 hoặc 3.
- Một CV không đủ dữ liệu để tạo `UNKNOWN`.
- Một CV trùng, một PDF scan và một PDF lỗi.
- Ba finalist phù hợp để comparison.
- Dataset/report benchmark final và một bản offline.

Không chọn dữ liệu quá hoàn hảo. File lỗi, duplicate và `UNKNOWN` chính là bằng chứng sản phẩm xử lý thế giới thực.

## Phương án dự phòng khi demo lỗi

| Sự cố | Câu chuyển | Hành động |
|---|---|---|
| Gemini/Internet lỗi | “Đây cũng là tình huống hệ thống được thiết kế để chịu được.” | Chỉ fallback badge và tiếp tục offline |
| Crawler lỗi | “Nguồn ngoài thay đổi không được phép làm hỏng hành trình chính.” | Dùng curated feed |
| Batch chạy chậm | “Trạng thái được lưu ở từng item; tôi chuyển sang batch đã chuẩn bị.” | Mở batch pre-seeded |
| PDF viewer lỗi | “Evidence vẫn giữ page và excerpt để kiểm chứng.” | Mở CV tab dự phòng/screenshot |
| Máy demo lỗi | “Đây là cùng release và dataset đã được ghi trong benchmark.” | Phát video offline |

Không xin lỗi dài và không cố sửa code trên sân khấu.

## Câu hỏi phản biện và câu trả lời ngắn

### “Điểm AI được tính như thế nào?”

“Điểm tổng là tổng có trọng số của kỹ năng, kinh nghiệm và học vấn theo criteria version đã publish. Mandatory gate được đánh giá riêng nên điểm cao không che được điều kiện bắt buộc.”

### “Gemini có phải toàn bộ AI của sản phẩm không?”

“Không. Semantic embedding và rule scoring là nền tảng; Gemini là reasoning/reranking tùy chọn. Khi không có Gemini, pipeline fallback vẫn chạy và benchmark ghi rõ chế độ.”

### “Nếu AI hallucinate thì sao?”

“Kết luận quan trọng phải có evidence. Không tìm thấy nguồn thì kết quả là UNKNOWN/manual review, không tự biến thành pass hoặc fail.”

### “Làm sao biết hệ thống tốt hơn keyword matching?”

“Chúng tôi so sánh trên cùng dataset/ground truth và công bố ranking agreement, evidence precision cùng cấu hình từng run. Chỉ dùng số từ benchmark final.”

### “Hệ thống có thiên lệch không?”

“Không mô hình nào được tuyên bố không thiên lệch tuyệt đối. Sản phẩm giảm rủi ro bằng blind review, criteria minh bạch, evidence, UNKNOWN, human override và theo dõi chất lượng theo version.”

### “Có dùng dữ liệu ứng viên để train không?”

“Không trong bản dự thi. Demo/benchmark dùng dữ liệu synthetic hoặc đã ẩn danh; CV không được dùng để huấn luyện nếu chưa có căn cứ và đồng ý phù hợp.”

### “Đây có phải production-ready không?”

“Đây là competition-ready, single-node prototype có test và recovery. Production cần identity provider, RBAC đầy đủ, encryption, malware scanning và hạ tầng worker riêng; các giới hạn được công bố rõ.”

### “Điểm khác biệt với ATS là gì?”

“Nhiều công cụ dừng ở ranking. Sản phẩm này quản trị criteria theo phiên bản, tách mandatory gate, đưa evidence về CV, biểu diễn thiếu dữ liệu bằng UNKNOWN và giữ riêng AI recommendation với human decision/audit.”

## Checklist diễn tập

- [ ] Lời thoại 6:00-6:30, không vượt 7 phút.
- [ ] Ba wow moment chạy liên tiếp không cần nhập dữ liệu dài.
- [ ] Metric đã thay placeholder bằng số benchmark final.
- [ ] Batch pre-seeded và batch live đều sẵn sàng.
- [ ] Online/offline mode đều đã chạy thử.
- [ ] Không có API key, notification, terminal history hoặc PII trên màn hình.
- [ ] Browser zoom/font phù hợp máy chiếu.
- [ ] Video offline mở được không cần mạng.
- [ ] Release SHA và dataset version xuất hiện trong slide/report.
- [ ] Mỗi thành viên biết phần nói và câu chuyển khi sự cố.
