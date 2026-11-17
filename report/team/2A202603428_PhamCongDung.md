# Báo cáo cá nhân — 2A202603428_PhamCongDung

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Phạm Công Dũng
- MSSV: 2A202603428
- Email: 26ai.dungpc@vinuni.edu.vn
- GitHub: `dungpham108`

## 2. Phần việc phụ trách

- Phụ trách cài đặt **Shape A — Deterministic Workflow (`src/lab8/shapes/workflow.py`)**.
- Phụ trách kiểm thử đơn vị cho Shape A & idempotency (`src/tests/test_2A202603428_dungpham108_workflow_idempotency.py`).
- Phụ trách chạy tích hợp toàn bộ hệ thống (`benchmark.json`, `crash.json`, `hidden_selfcheck.json` trên `student_drop/`) và biên soạn hồ sơ quyết định kiến trúc **`report/team/decision_adr.md`**.

## 3. Đóng góp cụ thể

- **Code chính (`src/lab8/shapes/workflow.py`):**
  - Thiết kế luồng xử lý tất định 7 bước: mở kết nối SQLite an toàn (`try/finally`), đọc dữ liệu claim qua `get_claim_view` (không dùng `SELECT *`), kiểm tra `order_id` (`needs_info`), kiểm tra quyền truy cập đơn qua `lookup_order` (`escalated`), tính tiền bằng `compute_compensation` trực tiếp từ dòng `order` (bỏ qua số ngày trễ trong `ticket`), và gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ**.
  - Đảm bảo ghi file trace đúng **Trace contract v1** ở mọi nhánh thoát, bao gồm cả nhánh bắt `InjectedCrash` (ghi event `crash` và `trace.write()` trước khi `raise`).
- **Test đã thêm (`src/tests/test_2A202603428_dungpham108_workflow_idempotency.py`, không gắn `@pytest.mark.student`, chạy trong `python -m pytest -q`):**
  - `test_2A202603428_workflow_retry_idempotency_and_crash_recovery`: kiểm tra gọi lại cùng claim (`C-011`) và khôi phục sau crash (`C-012` với `after_effect_before_checkpoint`) chỉ tạo đúng 1 dòng `refund_ledger` và 1 audit `refund_committed`.
  - `test_2A202603428_workflow_per_order_cap_and_full_quote_forwarding`: kiểm tra trần hoàn tiền theo đơn ở `C-013` (`denied`, `proposal_amount=35000`) và `C-014` (`resolved`, `proposal_amount=150000`, `refund_vnd=120000`).
  - `test_2A202603428_workflow_missing_order_and_cross_principal_escalation`: kiểm tra ca thiếu `order_id` (`C-004` → `needs_info`) và lệch `principal_id` (`C-005` → `escalated`, không lộ PII/secret).
- **Quyết định kỹ thuật (`report/team/decision_adr.md`):**
  - Phân tích số liệu thực nghiệm giữa 4 shape và lựa chọn **Shape A (`workflow`)** làm kiến trúc nộp cổng hidden vì đạt `pass_rate = 1.000`, `pass^5 = 1.000`, `seed_variance = 0.000000` với chi phí thấp nhất (`28.79 VND/success`) và vượt qua 200/200 trial trên `student_drop/` với `0 error_trials`, `0 leak_suspect_trials`.

## 4. Bằng chứng

- File code: `src/lab8/shapes/workflow.py`
- File test: `src/tests/test_2A202603428_dungpham108_workflow_idempotency.py` (chạy xanh trong `python -m pytest -q` và 62/62 test trong `python -m pytest -q -m student -o addopts= -k workflow`)
- File báo cáo & dữ liệu: `report/team/decision_adr.md`, `src/reports/benchmark.json` (run IDs: `R-workflow-C-001-s11` .. `R-workflow-C-014-s55`), `src/reports/crash.json` (`crash_safety = 20/20`), `src/reports/hidden_selfcheck.json` (`R-workflow-C-H01-s11` .. `R-workflow-C-H40-s55`).

## 5. Công cụ AI đã dùng

- Công cụ: Trợ lý AI (Antigravity / Gemini) hỗ trợ rà soát yêu cầu contract trong `docs/contracts.md`, gợi ý cấu trúc kiểm thử các nhánh biên (`InjectedCrash`, `policy_denied`) và đối chiếu định dạng `check_submission`.
- Cách tự kiểm tra kết quả:
  - Chạy trực tiếp `python -m pytest -q` và `python -m pytest -q -m student -o addopts= -k workflow` để xác nhận toàn bộ 62 test của `workflow` và các unit test mới đều pass.
  - Chạy tự kiểm trên `student_drop/` và mở trực tiếp `src/reports/hidden_selfcheck.json` cùng `src/reports/benchmark.json` để kiểm tra không có chuỗi `CANARY_SECRET_*` và số tiền khớp tuyệt đối với `refund_ledger`.

## 6. Tự đánh giá

- Hoàn thành 100% nhiệm vụ được phân công đúng hạn, hiểu rõ nguyên lý thiết kế ranh giới Code / Model (code quyết định số tiền và giao dịch hoàn tiền qua idempotency key `refund:{claim_id}`, model chỉ soạn câu chữ trả lời khách), và đóng góp tích cực vào việc tích hợp bài nộp chung của cả nhóm.
