# Hướng dẫn phát hành bản dự thi

## Release gate

Chỉ phát hành từ commit đã merge vào `main`. Working tree phải sạch và toàn bộ CI, benchmark offline, release safety, clean-room cùng showcase E2E phải xanh.

```powershell
git status --short
./scripts/check_open_source_compliance.ps1
./scripts/check_release_safety.ps1
./scripts/verify_clean_room.ps1 -SourceMode Archive -RecordPath release/clean-room-result.json
```

Không tạo tag từ feature branch. Không đưa `.env`, database, CV/PDF, thư mục storage, output sinh ra hoặc dữ liệu ứng viên thật vào source artifact.

## Manifest và checksum

Manifest release phải ghi tối thiểu version/tag, full commit SHA, source archive/SHA-256, CI URL, test counts, benchmark lineage, SBOM/license inventory, clean-room environment, demo assets và known limitations.

```powershell
git archive --format=tar.gz --output=release/resume-screening-ai-1.1.0.tar.gz v1.1.0
Get-FileHash release/resume-screening-ai-1.1.0.tar.gz -Algorithm SHA256 |
  Format-List Algorithm,Hash,Path
```

Đối chiếu checksum sau khi tải artifact từ GitHub Release, không chỉ kiểm tra file local.

## SBOM và giấy phép

- `DEPENDENCIES.md` là inventory dependency trực tiếp đã review.
- `frontend/package-lock.json` khóa dependency Node; `backend/requirements.txt` là đầu vào môi trường Python.
- `backend/requirements-optional.txt` bổ sung sentence-transformer và live crawler cho môi trường online; không cần cho clean-room offline.
- Sinh SPDX SBOM frontend bằng `npm sbom --sbom-format spdx` và lưu làm release asset.
- Lưu output `python -m pip freeze` cùng SBOM để tái tạo chính xác môi trường Python.
- Không phát hành model weights nếu chưa có model card/license tương ứng.

## Offline fallback

```dotenv
OFFLINE_MODE=true
OFFLINE_ENGINE=deterministic-keyword-v1
DISABLE_EMBEDDING_MODEL=true
GEMINI_API_KEY=
```

Trong chế độ này backend không tải sentence-transformer, không gọi Gemini và crawler trả bộ việc làm demo cục bộ. Thanh điều hướng phải hiển thị `Offline · deterministic-keyword-v1`.

## Trình tự phát hành

1. Merge các slice đã review vào `main` và chạy full CI.
2. Chạy benchmark final và clean-room từ chính commit ứng viên.
3. Chốt changelog, verification record, SBOM, checksum và limitations.
4. Tạo annotated tag `v1.1.0` trỏ đúng commit `main`.
5. Tạo draft GitHub Release, tải source, checksum, SBOM, benchmark và demo assets.
6. Tải lại artifact, xác minh checksum, smoke test ở đường dẫn mới rồi kiểm tra link khi không đăng nhập.

## Giới hạn production

Bản thi là single-node dùng SQLite và local storage. Header role chỉ phục vụ prototype; triển khai doanh nghiệp cần identity provider và authorization policy thật. OCR chuyên dụng chưa bắt buộc, manual verified-text là recovery path. Benchmark synthetic không phải cam kết accuracy trên CV thật.
