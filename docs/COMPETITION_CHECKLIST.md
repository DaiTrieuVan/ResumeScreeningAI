# Open Source AI Competition 2026 Checklist

Checklist nội bộ đối chiếu thể lệ. Chỉ đánh dấu hoàn tất sau khi kiểm tra trên
GitHub/default branch và máy sạch, không chỉ trong working tree cá nhân.

## Evidence index

- AI metrics và cách tái hiện: [`AI_EVALUATION.md`](AI_EVALUATION.md)
- Build/release procedure: [`RELEASE_GUIDE.md`](RELEASE_GUIDE.md)
- Machine-clean-room record: [`../release/verification-record.md`](../release/verification-record.md)
- Regression commands và acceptance journeys: [`TESTING.md`](TESTING.md)
- Responsible AI và Blind Review: [`PRIVACY_AND_RESPONSIBLE_AI.md`](PRIVACY_AND_RESPONSIBLE_AI.md)

## A. Điều kiện và lịch

- [ ] Thành viên đều là sinh viên ICTU; nhóm tối đa 3 người.
- [ ] Đã đăng ký trước 30/06/2026.
- [ ] Đã chuẩn bị phiếu và link kho mã nguồn để nộp từ 01/07 đến 30/09/2026.
- [ ] Nhóm có thể tham gia chung kết/hackathon dự kiến 10/10/2026.

## B. Proof of Freedom - 50 điểm

### 1. Source control - 5 điểm

- [x] Repository GitHub có web viewer và đang public.
- [x] Lịch sử commit/branch thể hiện repository thực sự được sử dụng.
- [ ] Nhánh tài liệu và Recruiter Workspace đã merge vào default branch `main`.

### 2. OSI-approved license - 10 điểm

- [x] Có toàn văn MIT License trong `LICENSE`.
- [x] README nêu mục đích và giấy phép.
- [x] Có `NOTICE` và danh mục dependency/license.
- [x] SPDX header tồn tại trong mọi tệp mã nguồn do dự án sở hữu.
- [ ] Chạy kiểm kê license/SBOM và xử lý mọi dependency không tương thích.

### 3. Versioned release - 5 điểm

- [x] Có GitHub Release theo Semantic Versioning.
- [ ] Tạo release mới từ `main` chứa toàn bộ bản dự thi.
- [ ] Đính kèm/ưu tiên source `.tar.gz`, checksum và release notes.
- [ ] Clone release artifact và xác nhận SHA/version.

### 4. Build from source - 10 điểm

- [x] Có hướng dẫn Windows và Linux/macOS.
- [x] Không cần IDE/compiler nguồn đóng.
- [x] Có `.env.example` và không sửa header/source để cấu hình.
- [x] Chạy clean-room build từ committed Git archive theo `docs/BUILD_AND_DEPLOYMENT.md`.
- [x] Xác nhận chạy sau khi đổi đường dẫn thư mục source (working-tree snapshot).
- [ ] Xác nhận production reverse proxy `/api` hoạt động.

### 5. Dependencies/bundling - 10 điểm

- [x] Dependency cài qua `pip`/`npm`, không bundle source đã sửa.
- [x] `DEPENDENCIES.md` liệt kê direct runtime/test dependencies.
- [x] `package-lock.json` được track.
- [ ] Sinh SBOM/license report cho release chính thức.
- [ ] Ghi model card/license nếu redistributing model weights.

### 6. Documentation and communication - 10 điểm

- [x] README, build guide, architecture, AI, testing và privacy docs.
- [x] CHANGELOG theo Keep a Changelog/SemVer.
- [x] GitHub Issues được cấu hình làm bug tracker.
- [x] Có issue/PR templates, contributing, security và code of conduct.
- [ ] Tạo và đóng issue thật để chứng minh workflow quản lý lỗi.
- [ ] Kiểm tra toàn bộ link trên GitHub sau merge.

## C. Product - 50 điểm

### Originality - 10 điểm

- [ ] Chuẩn bị slide so sánh với ATS/resume matcher phổ biến.
- [ ] Nhấn mạnh criteria versioning, evidence, UNKNOWN, human decision và audit.

### Completeness - 10 điểm

- [x] Backend/frontend tests và production build xanh trên feature branch.
- [ ] Chạy clean-room demo từ release artifact.
- [ ] Chuẩn bị dữ liệu demo offline và video dự phòng.
- [ ] Kiểm tra Gemini enabled/disabled và crawler failure.

### Usability - 10 điểm

- [x] Có responsive/keyboard/drawer-scrolling E2E.
- [ ] Test trên laptop và máy chiếu dùng tại chung kết.
- [ ] Hoàn thiện onboarding hoặc nút dùng dữ liệu mẫu.

### AI integration - 10 điểm

- [x] Có semantic matching, optional Gemini và deterministic fallback.
- [x] Có criteria/evidence/model metadata documentation.
- [x] Chạy evaluation dataset và điền số đo thực tế; không dùng target như result.
- [x] Ghi model, prompt, criteria và dataset version trong showcase.

### Presentation/community - 10 điểm

- [x] Có demo script và anticipated Q&A.
- [ ] Thêm repository description, homepage và topics.
- [ ] Thêm screenshots/GIF/video, architecture diagram render và live demo link.
- [ ] Tạo issues `good first issue`/roadmap và mời phản hồi cộng đồng.
- [ ] Tập demo 5-7 phút và chuẩn bị bản offline.

## D. Release gate

- [x] Không có secret, PII, CV thật, DB hoặc output nhạy cảm trong snapshot đã scan.
- [x] Backend tests xanh trên clean-room snapshot.
- [x] Frontend unit tests, E2E và build xanh trên clean-room snapshot.
- [x] License/dependency scan đã review; npm audit hiện có 0 vulnerability.
- [ ] `CHANGELOG.md` chuyển `[Unreleased]` thành version/date.
- [ ] Tag annotated trỏ đúng `main` commit.
- [ ] GitHub Release công khai trước hạn nộp và source `.tar.gz` tải được.
- [ ] Form nộp chứa đúng repository/release/demo links.
