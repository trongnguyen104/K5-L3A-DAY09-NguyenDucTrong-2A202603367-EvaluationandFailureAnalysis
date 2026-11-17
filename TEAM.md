# Team

## Thông tin nhóm

- Tên nhóm: Apollo
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Apollo-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: `https://github.com/dungpham108/K5-L3A-DAY08-Apollo-FromWorkflowsToAgents.git` (branch `main`, commit `034c6c4`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Phạm Công Dũng | 2A202603428 | 26ai.dungpc@vinuni.edu.vn | dungpham108 | Shape A (`workflow.py`) + Integration, Benchmark, Crash Suite, Hidden Self-check & ADR (`decision_adr.md`) |
| 2 | Trần Thanh Tùng | 2A202603418 | 26ai.tungtt@vinuni.edu.vn | tungtran306 | Shape B (`single.py` ReAct) + Policy/Approval Verification & Research Card (`research_card.md`) |
| 3 | Nguyễn Đức Trọng | 2A202603367 | 26ai.trongnd3@vinuni.edu.vn | trongnguyen104 | Shape C (`orchestrator.py` + Handoff Security) + Trace Audit, Bonus B3 (`swarm_verified.py`) & Group Report |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa (ghi rõ tên file + tên hàm test, không gắn marker `@pytest.mark.student` để chạy trong cổng host `python -m pytest -q`).

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Công Dũng (`dungpham108`) | Shape A (`workflow.py`), tích hợp hệ thống, chạy benchmark, crash suite & `student_drop` self-check, soạn `decision_adr.md` | `54edb0d` | `src/tests/test_2A202603428_dungpham108_workflow_idempotency.py`: `test_2A202603428_workflow_retry_idempotency_and_crash_recovery`, `test_2A202603428_workflow_per_order_cap_and_full_quote_forwarding`, `test_2A202603428_workflow_missing_order_and_cross_principal_escalation` |
| Trần Thanh Tùng (`tungtran306`) | Shape B (`single.py` ReAct agent), kiểm thử chống prompt injection/ticket lie & chặn approval mượn/hết hạn, soạn `research_card.md` | `403f99c` | `src/tests/test_2A202603418_tungtran306_single_policy.py`: `test_2A202603418_single_react_ignores_ticket_delay_lie_on_all_seeds`, `test_2A202603418_single_react_blocks_borrowed_and_expired_approvals`, `test_2A202603418_single_react_resists_prompt_injection_and_respects_step_cap` |
| Nguyễn Đức Trọng (`trongnguyen104`) | Shape C (`orchestrator.py` + `handoff.v1`), kiểm toán trace/PII, Bonus B3 (`bonus/swarm_verified.py`), soạn `group_report.md` & `bonus_report.md` | `bc3f3d7` | `src/tests/test_2A202603367_trongnguyen104_orchestrator_handoff.py`: `test_sv03_orchestrator_handoff_allowlist_and_secret_redaction`, `test_sv03_orchestrator_stacking_and_partial_approval_cap`, `test_sv03_orchestrator_crash_propagation_and_resume` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603428_PhamCongDung

### Phần việc phụ trách

- Thiết kế và cài đặt **Shape A (`src/lab8/shapes/workflow.py`)** theo luồng Python cố định (deterministic workflow).
- Tích hợp 4 shape, chạy bộ kiểm thử `crash_test` (`src/reports/crash.json`), `benchmark` (`src/reports/benchmark.json`) và tự kiểm trên bộ hidden không nhãn `student_drop/` (`src/reports/hidden_selfcheck.json`).
- Viết hồ sơ quyết định kiến trúc `report/team/decision_adr.md`.

### Đóng góp cụ thể

- Cài đặt `run_claim` trong `src/lab8/shapes/workflow.py`: đọc dữ liệu qua allowlist `get_claim_view` và `lookup_order`, tính tiền bằng `compute_compensation`, chuyển tiếp quote đầy đủ cùng `crash_at` vào `durability.issue_refund`, ghi trace chuẩn Contract v1 ở mọi nhánh trả về.
- Viết bộ unit test `src/tests/test_2A202603428_dungpham108_workflow_idempotency.py` (không gắn `@pytest.mark.student`, chạy trực tiếp trong cổng host `python -m pytest -q`) gồm 3 hàm: `test_2A202603428_workflow_retry_idempotency_and_crash_recovery`, `test_2A202603428_workflow_per_order_cap_and_full_quote_forwarding`, `test_2A202603428_workflow_missing_order_and_cross_principal_escalation`.

### Bằng chứng

- Code: `src/lab8/shapes/workflow.py`
- Test: `src/tests/test_2A202603428_dungpham108_workflow_idempotency.py`
- Report: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/hidden_selfcheck.json`, `report/team/decision_adr.md`

## 2A202603418_TranThanhTung

### Phần việc phụ trách

- Thiết kế và cài đặt **Shape B (`src/lab8/shapes/single.py`)** sử dụng vòng lặp `run_react` với `max_steps=8` và `worker=True`.
- Đảm bảo tác tử ReAct chỉ gọi công cụ đọc (`READONLY_TOOLS`), không tin số ngày trễ hay điều khoản cũ trong `ticket`, và giao toàn quyền ghi ledger cho host sau vòng lặp.
- Thực hiện nghiên cứu và phân tích ablation trong `report/team/research_card.md`.

### Đóng góp cụ thể

- Cài đặt hàm `decide(obs)` trong `src/lab8/shapes/single.py` điều phối tuần tự `lookup_order` → `lookup_refund_history` → `compute_compensation`, ghi nhận đầy đủ `Budget` (model calls và tool calls) và trace Contract v1.
- Viết bộ unit test `src/tests/test_2A202603418_tungtran306_single_policy.py` (chạy trong cổng host `python -m pytest -q`) gồm 3 hàm: `test_2A202603418_single_react_ignores_ticket_delay_lie_on_all_seeds`, `test_2A202603418_single_react_blocks_borrowed_and_expired_approvals`, `test_2A202603418_single_react_resists_prompt_injection_and_respects_step_cap`.

### Bằng chứng

- Code: `src/lab8/shapes/single.py`
- Test: `src/tests/test_2A202603418_tungtran306_single_policy.py`
- Report: `report/team/research_card.md`, `src/reports/benchmark.json`, `src/reports/hidden_selfcheck.json`

## 2A202603367_NguyenDucTrong

### Phần việc phụ trách

- Thiết kế và cài đặt **Shape C (`src/lab8/shapes/orchestrator.py`)** kết hợp `make_handoff` và `run_readonly_investigators`.
- Kiểm toán bảo mật handoff và trace (ngăn chặn rò rỉ `CANARY_SECRET_*`, `raw_headers`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ).
- Phát triển phần **Bonus B3 (`src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`)** và tổng hợp `report/team/group_report.md`, `report/team/bonus_report.md`.

### Đóng góp cụ thể

- Cài đặt `src/lab8/shapes/orchestrator.py`: tạo gói `handoff.v1` qua allowlist, chạy investigator chỉ đọc, tính quote từ dữ liệu có cấu trúc và gọi `durability.issue_refund` tại orchestrator.
- Cài đặt `src/bonus/swarm_verified.py` bổ sung tầng code verifier chặn lỗi khuếch đại từ `model_override` ở seed chia hết cho 5; xây dựng 8 ca đối kháng trong `src/bonus/cases.jsonl`.
- Viết `src/tests/test_2A202603367_trongnguyen104_orchestrator_handoff.py` (`test_2A202603367_orchestrator_handoff_allowlist_and_secret_redaction`, `test_2A202603367_orchestrator_stacking_and_partial_approval_cap`, `test_2A202603367_orchestrator_crash_propagation_and_resume`) và `src/tests/test_bonus_swarm_verified.py`.

### Bằng chứng

- Code: `src/lab8/shapes/orchestrator.py`, `src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`
- Test: `src/tests/test_2A202603367_trongnguyen104_orchestrator_handoff.py`, `src/tests/test_bonus_swarm_verified.py`
- Report: `report/team/group_report.md`, `report/team/bonus_report.md`, `src/reports/bonus_benchmark.json`, `src/reports/bonus_adversarial.json`, `src/reports/hidden_selfcheck.json`