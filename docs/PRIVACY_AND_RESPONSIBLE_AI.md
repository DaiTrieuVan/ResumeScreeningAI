# Privacy and Responsible AI

## Mục đích và phạm vi

Ứng dụng xử lý CV để hỗ trợ so khớp với một JD cụ thể, giải thích tiêu chí và quản
lý quy trình tuyển dụng. Không dùng dữ liệu cho quảng cáo, nhận diện sinh trắc học
hoặc huấn luyện model nếu chưa có căn cứ pháp lý và sự đồng ý phù hợp.

## Dữ liệu được xử lý

- CV gốc và tên file;
- tên, email, số điện thoại trích xuất;
- kỹ năng, kinh nghiệm, học vấn;
- embedding, điểm, evidence và giải thích;
- stage, ghi chú, quyết định và audit metadata.

CV, email, điện thoại, raw text và evidence là dữ liệu nhạy cảm. Log không được
chứa raw CV hoặc PII không cần thiết.

## Nguyên tắc

1. **Purpose limitation**: chỉ dùng cho job/workflow người dùng lựa chọn.
2. **Data minimization**: chỉ lưu trường cần thiết; export theo mục đích.
3. **Human oversight**: AI recommendation không phải quyết định cuối.
4. **Transparency**: hiển thị criteria, evidence, confidence và thiếu dữ liệu.
5. **Contestability**: recruiter có thể override; lịch sử giữ AI và human decision riêng.
6. **Retention**: tổ chức triển khai phải đặt thời hạn lưu và xóa/ẩn danh đúng hạn.
7. **Security**: least privilege, TLS, secret management, backup có kiểm soát.

## Access và audit

Các vai trò prototype được phép xem PII gồm recruiter, hiring manager và admin.
Xem detail, mở CV gốc, export và anonymize tạo `AuditEvent` không chứa nội dung CV.
Không xem header role hiện tại là authentication production; cần identity provider
và mapping quyền phía server khi triển khai thật.

## Anonymization

Luồng anonymization:

- xóa file CV trong storage root;
- xóa tên/email/điện thoại/raw text và dữ liệu cấu trúc;
- xóa evidence snippet;
- làm sạch AI summaries, recruiter notes và decision notes có thể chứa PII;
- dùng pseudonym ổn định từ application ID;
- giữ audit nghiệp vụ tối thiểu không chứa nội dung cá nhân.

Backup cũng phải tuân theo retention; xóa record chính không tự động xóa bản backup cũ.

## Quy tắc tuyển dụng có trách nhiệm

- Không dùng thuộc tính được bảo vệ hoặc proxy của chúng để chấm điểm.
- Không auto-reject chỉ dựa vào overall score.
- Mandatory criterion cần bằng chứng hoặc manual review.
- Điều tra định kỳ override rate theo nhóm dữ liệu hợp pháp và đã ẩn danh.
- Cho phép sửa dữ liệu trích xuất sai trước khi ra quyết định.
- Ghi rõ model có thể sai, hallucinate hoặc bỏ sót cách diễn đạt khác biệt.

## Dữ liệu demo và phát triển

Chỉ dùng CV tổng hợp hoặc đã ẩn danh. Không commit `.env`, DB, storage, export,
screenshot có PII hoặc log từ production. Fixture nên dùng tên/email giả thuộc
domain `example.com`.

## Checklist production

- [ ] Authentication và server-side RBAC
- [ ] TLS và encryption at rest
- [ ] Secret manager; không dùng key trong source/client
- [ ] Upload size/type validation và malware scanning
- [ ] Rate limiting và audit retention
- [ ] Chính sách consent/retention được tổ chức phê duyệt
- [ ] Quy trình access/correction/deletion request
- [ ] Backup/restore và secure deletion được kiểm chứng
- [ ] Bias/evidence evaluation được ghi nhận theo model version
