# Báo cáo cá nhân — SV03_NguyenDucTrong

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Trọng
- MSSV: 2A202603367
- Email: trongnguyen104@gmail.com
- GitHub: `trongnguyen104`

## 2. Phần việc phụ trách

- Phụ trách cài đặt **Shape C — Orchestrator + Read-Only Investigators (`src/lab8/shapes/orchestrator.py`)**.
- Phụ trách kiểm thử đơn vị cho Shape C và ranh giới bảo mật handoff/trace (`src/tests/test_SV03_trongnguyen104_orchestrator_handoff.py`).
- Phụ trách cài đặt phần mở rộng **Bonus B3 — Verifier chống khuếch đại lỗi (`src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`, `src/tests/test_bonus_swarm_verified.py`)** và tổng hợp **`report/team/group_report.md`**, **`report/team/bonus_report.md`**.

## 3. Đóng góp cụ thể

- **Code chính (`src/lab8/shapes/orchestrator.py`):**
  - Xây dựng luồng điều phối phân tách quyền hạn: Orchestrator đọc `get_claim_view`, tạo gói chuyển giao `handoff.v1` qua `lab8.handoff.make_handoff` chỉ cấp quyền các công cụ đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`) và không truyền `parent_secret`, `raw_headers` hay dòng `claim` thô vào `facts`.
  - Gọi `lab8.runtime.run_readonly_investigators` để thu thập dữ liệu đã lọc theo `principal_id`, ghi nhận gói handoff đã sanitize vào trace (`trace.add("handoff", safe_dump(handoff))`), sau đó tính quote từ dữ liệu có cấu trúc và gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` tại orchestrator.
- **Code Bonus B3 (`src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`):**
  - Bổ sung bước **code verifier** vào sau bước báo giá của `swarm` để đối chiếu `delay_days`, `status`, `damage_verified` với `structured_order`. Khi phát hiện sai lệch (do `model_override` ở `seed % 5 == 0`), verifier ghi event `verifier_override`, tính lại quote đúng 1 lần từ dữ liệu chuẩn và chặn hoàn toàn lỗi trả tiền sai.
  - Thiết kế 8 ca kiểm thử đối kháng có nhãn viết tay trong `src/bonus/cases.jsonl` và `src/bonus/world.json`.
- **Test đã thêm (`src/tests/test_SV03_trongnguyen104_orchestrator_handoff.py` và `src/tests/test_bonus_swarm_verified.py`, không gắn `@pytest.mark.student`, chạy trong `python -m pytest -q`):**
  - `test_sv03_orchestrator_handoff_allowlist_and_secret_redaction`: kiểm tra gói handoff trong trace chỉ chứa các khóa thuộc `ALLOWED_FIELDS` và công cụ thuộc `READONLY_TOOLS`, đồng thời không rò rỉ bất kỳ chuỗi `forbid_substrings` nào (`CANARY_SECRET_*`, SĐT, địa chỉ, mặt hàng, ghi chú nội bộ).
  - `test_sv03_orchestrator_stacking_and_partial_approval_cap`: kiểm tra trần hoàn tiền theo đơn và approval thấp hơn quote trên `orchestrator` (`C-008`, `C-014`).
  - `test_sv03_orchestrator_crash_propagation_and_resume`: kiểm tra truyền `crash_at` và khôi phục sau crash trên `orchestrator` (`C-012`).
  - `test_bonus_verifier_overrides_swarm_weakness_on_public_t02` & `test_bonus_adversarial_pack_passes_all_cases_and_seeds`: kiểm tra `swarm_verified` sửa lỗi `C-002` ở seed 55 và đạt 100% pass trên bộ 8 ca đối kháng.

## 4. Bằng chứng

- File code: `src/lab8/shapes/orchestrator.py`, `src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`
- File test: `src/tests/test_SV03_trongnguyen104_orchestrator_handoff.py`, `src/tests/test_bonus_swarm_verified.py` (chạy xanh trong `python -m pytest -q` và 62/62 test trong `python -m pytest -q -m student -o addopts= -k orchestrator`)
- File báo cáo & dữ liệu: `report/team/group_report.md`, `report/team/bonus_report.md`, `src/reports/benchmark.json`, `src/reports/bonus_benchmark.json`, `src/reports/bonus_adversarial.json`, `src/reports/hidden_selfcheck.json`.

## 5. Công cụ AI đã dùng

- Công cụ: Trợ lý AI (Antigravity / Gemini) hỗ trợ rà soát cơ chế allowlist trong `src/lab8/handoff.py`, thiết kế dữ liệu kiểm thử đối kháng cho Bonus B3 và trình bày báo cáo nhóm.
- Cách tự kiểm tra kết quả:
  - Chạy `python -m pytest -q -m student -o addopts= -k orchestrator` (62 passed) và `python -m pytest -q` (69 passed).
  - Chạy `python -m lab8.check_submission` để xác minh định dạng toàn bộ báo cáo, bảng đóng góp và các file JSON trong `src/reports/`.

## 6. Tự đánh giá

- Hoàn thành tốt nhiệm vụ cài đặt Shape C (`orchestrator.py`), kiểm toán an toàn thông tin trên trace/handoff, phát triển thành công phần điểm cộng B3 (`swarm_verified`) và phối hợp chặt chẽ với hai thành viên còn lại để hoàn thiện báo cáo nhóm.