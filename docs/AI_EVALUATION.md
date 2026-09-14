# Đánh giá AI cho bản dự thi

## Mục đích

Benchmark `competition-v1` kiểm tra khả năng tái lập của pipeline đánh giá trong chế độ offline. Bộ dữ liệu gồm 3 JD và 30 hồ sơ tổng hợp, không mô tả người thật. Kết quả này chứng minh công thức metric, lineage và fallback hoạt động; không được diễn giải thành độ chính xác trên thị trường lao động thực tế.

## Chạy lại benchmark

Từ thư mục gốc repository:

```powershell
$commit = git rev-parse --short HEAD
backend\venv\Scripts\python.exe scripts\run_ai_benchmark.py `
  --dataset competition-v1 `
  --release-version 1.1.0-competition `
  --commit-sha $commit
```

Trên Linux/macOS, thay đường dẫn Python bằng interpreter của virtual environment. Runner ghi `artifacts/benchmark/competition-v1.json` và `.md`; thư mục này không được Git theo dõi để tránh nhầm báo cáo cũ với kết quả release mới. Bản final phải được đính kèm vào GitHub Release và ghi checksum trong release manifest.

## Metric và ngưỡng

| Metric | Ý nghĩa | Ngưỡng release |
|---|---|---:|
| Mandatory recall | Tỷ lệ yêu cầu bắt buộc dương tính được nhận diện | ≥ 0,90 |
| Evidence precision | Tỷ lệ evidence dự đoán được ground truth xác nhận | ≥ 0,90 |
| UNKNOWN accuracy | Tỷ lệ trường hợp thiếu dữ liệu được giữ là `UNKNOWN` | ≥ 0,95 |
| Ranking agreement | Tỷ lệ cặp ứng viên có thứ tự khớp chuyên gia | ≥ 0,70 |
| Batch completion | Tỷ lệ hồ sơ có trạng thái kết thúc hoặc recovery rõ ràng | 1,00 |

Mỗi metric phải có numerator, denominator, value, threshold và status. Denominator bằng 0 là lỗi đánh giá, không phải một kết quả đạt.

## Cách đọc kết quả

- `PASSED` chỉ có nghĩa tất cả metric của dataset/version được nêu đã đạt ngưỡng.
- Luôn đối chiếu `release.commit_sha`, dataset version, criteria versions, model, prompt và fallback mode.
- Không dùng target làm số đo thực tế và không sửa nhãn để làm đẹp kết quả.
- Khi một metric fail, dừng release, ghi các case ID gây lỗi và chỉ chạy lại sau khi có sửa lỗi cùng regression test.

## Giới hạn công bố

Baseline hiện dùng dữ liệu synthetic và deterministic fallback. Nó phù hợp để chứng minh reproducibility, xử lý `UNKNOWN`, evidence và ranking plumbing. External-validity trên CV ẩn danh được gán nhãn độc lập vẫn là gate triển khai thực tế trong tương lai. AI chỉ hỗ trợ quyết định; hệ thống không tự động từ chối ứng viên.
