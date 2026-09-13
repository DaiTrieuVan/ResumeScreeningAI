# Security Policy

## Phạm vi hỗ trợ

Nhánh `main` và bản phát hành mới nhất được hỗ trợ sửa lỗi bảo mật. Các bản cũ
chỉ được cập nhật khi lỗ hổng có mức ảnh hưởng nghiêm trọng.

## Báo cáo lỗ hổng

Không đăng CV thật, API key, dữ liệu cá nhân hoặc chi tiết khai thác công khai
trong GitHub Issues. Hãy liên hệ riêng với maintainer qua địa chỉ bảo mật sẽ
được công bố trong phần Contact của repository trước khi phát hành chính thức.

Trong báo cáo, vui lòng cung cấp:

- phiên bản hoặc commit bị ảnh hưởng;
- điều kiện tái hiện tối thiểu;
- tác động dự kiến;
- log đã loại bỏ dữ liệu cá nhân;
- đề xuất giảm thiểu nếu có.

Maintainer sẽ xác nhận tiếp nhận, phân loại mức độ và phối hợp thời điểm công bố.

## Dữ liệu nhạy cảm

- Không commit `.env`, database, CV, file export hoặc khóa truy cập.
- Chỉ dùng CV tổng hợp/đã ẩn danh cho demo và test.
- Thu hồi ngay khóa Gemini nếu nghi ngờ bị lộ.
- Người triển khai chịu trách nhiệm cấu hình xác thực thật trước khi dùng trong tổ chức.

Xem thêm `docs/PRIVACY_AND_RESPONSIBLE_AI.md`.
