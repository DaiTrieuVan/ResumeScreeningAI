# Contributing to Resume Screening AI

Cảm ơn bạn quan tâm đến dự án. Mọi đóng góp về mã nguồn, tài liệu, kiểm thử,
khả năng tiếp cận và tuyển dụng có trách nhiệm đều được hoan nghênh.

## Trước khi bắt đầu

1. Đọc `README.md`, `docs/ARCHITECTURE.md` và `docs/PRIVACY_AND_RESPONSIBLE_AI.md`.
2. Tìm issue hiện có trước khi tạo issue mới.
3. Với thay đổi lớn, tạo issue mô tả vấn đề, phạm vi và tiêu chí nghiệm thu trước.
4. Không đưa CV thật, API key, email, số điện thoại hoặc dữ liệu tuyển dụng riêng tư vào repository.

## Quy trình đóng góp

1. Fork repository và tạo nhánh từ `develop`.
2. Đặt tên nhánh theo dạng `feature/mo-ta-ngan`, `fix/mo-ta-ngan` hoặc `docs/mo-ta-ngan`.
3. Cài đặt và chạy dự án theo `docs/BUILD_AND_DEPLOYMENT.md`.
4. Viết hoặc cập nhật test tương ứng với thay đổi.
5. Chạy toàn bộ lệnh kiểm tra trước khi mở pull request.
6. Cập nhật `CHANGELOG.md` nếu thay đổi ảnh hưởng người dùng hoặc API.
7. Mở pull request bằng template có sẵn và liên kết issue liên quan.

## Chuẩn commit

Dự án sử dụng Conventional Commits:

```text
feat(recruiter): add evidence-backed comparison
fix(upload): keep successful items when retrying a batch
docs(ai): explain local fallback behavior
test(api): cover optimistic update conflicts
```

Mỗi commit nên giải quyết một mục đích độc lập, có thể review và hoàn tác riêng.

## Kiểm tra bắt buộc

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm test -- --run
npm run test:e2e
npm run build
```

## License của đóng góp

Bằng việc gửi đóng góp, bạn đồng ý cấp phép phần đóng góp đó theo MIT License
của dự án. Tệp mã nguồn mới phải chứa:

```text
SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
SPDX-License-Identifier: MIT
```

Hãy dùng cú pháp comment hợp lệ của ngôn ngữ tương ứng.
