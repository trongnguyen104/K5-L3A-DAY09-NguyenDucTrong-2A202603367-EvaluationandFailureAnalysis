# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: e425386
- Run id dẫn chứng: R-workflow-C-001-s11, R-workflow-C-002-s55, R-swarm-C-002-s55, R-workflow-C-014-s11
- Pass rate / pass^5 / seed min-max / variance: pass_rate=1.000 (70/70) / pass^5=1.000 (14/14) / seed min-max=1.000-1.000 / variance=0.000000 (src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.79 VND (2015.00 VND / 70 trial pass; mean_steps=2.79, p95_steps=3.0)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: secret_leak=0, pii_leak=0, approval_bypass=0 (public benchmark & 200/200 trial trên student_drop/ trong src/reports/hidden_selfcheck.json có leak_suspect_trials=0, error_trials=0)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng tập 14 claim public (`C-001` đến `C-014`) × 5 seed (`11, 22, 33, 44, 55`) = 70 trial độc lập trong `src/reports/benchmark.json`, ba kiến trúc do nhóm xây dựng (`workflow`, `single`, `orchestrator`) đều đạt `pass_rate = 1.000`, `pass^5 = 1.000` và `seed_variance = 0.000000`, trong khi `swarm` tham chiếu chỉ đạt `pass_rate = 0.986` (69/70), `pass^5 = 0.929` (13/14) và `seed_variance = 0.000816` do trượt `R-swarm-C-002-s55` (tin số ngày trễ 5 ngày ghi trong ticket thay vì 2 ngày trong DB). Khi chất lượng đầu ra và độ an toàn (`crash_safety = 20/20`, `secret_leak = 0`, `approval_bypass = 0`) ngang nhau giữa A, B và C, nguyên tắc chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành công việc chỉ thẳng về **Shape A (`workflow`)**: chi phí mô phỏng thấp nhất (**28.79 VND/success**, rẻ hơn `single` 26.5% ở mức 39.15 VND, rẻ hơn `swarm` 41.9% ở mức 49.57 VND và rẻ hơn `orchestrator` 49.5% ở mức 57.05 VND), số bước trung bình thấp nhất (`mean_steps = 2.79`, `p95_steps = 3.0`), trung bình chỉ gọi 1.0 model call (soạn thông báo) và 2.79 tool calls mỗi trial. Quy trình nghiệp vụ hoàn phí của LogiX-VN có cấu trúc đầu vào rõ ràng (`order_id`, `principal_id`, `delay_days`, `damage_verified`) và công thức tính tiền cố định (`compute_compensation`), nên việc giữ luồng điều khiển trong code Python giúp loại bỏ hoàn toàn rủi ro lệch mục tiêu hoặc khuếch đại lỗi từ LLM.

## Có đáng đổi lấy multi-agent không

Trong bài toán hoàn phí LogiX-VN hiện tại, **không đáng** đánh đổi từ `workflow` sang multi-agent (`orchestrator` hoặc `swarm`). So với `workflow`, `orchestrator` làm tăng chi phí trên mỗi lần thành công từ 28.79 VND lên 57.05 VND (+98.2% chi phí) và tăng số lần gọi tool từ 2.79 lên 5.57 do chi phí khởi tạo handoff và đọc lại dữ liệu ở investigator, nhưng không cải thiện thêm `pass_rate` (vẫn là 1.000). Thậm chí với `swarm`, việc thêm các cuộc gọi `peer` và `parse` không những làm tăng chi phí lên 49.57 VND mà còn mở ra bề mặt tấn công/nhiễu mới khi model tự ý ghi đè dữ kiện có cấu trúc (`R-swarm-C-002-s55`), kéo `pass^5` xuống 0.929 và tạo phương sai `0.000816`.

Quyết định kiến trúc sẽ **đảo lại** (chuyển sang `single` ReAct hoặc `orchestrator` + read-only investigators) khi và chỉ khi thỏa mãn ít nhất một trong các điều kiện sau:

1. **Đầu vào phi cấu trúc thực sự quyết định việc định tuyến tool:** Ví dụ claim không có sẵn cột `order_id` hoặc loại sự cố trong DB mà phải trích xuất từ nhiều nguồn tài liệu không đồng nhất (email đính kèm, biên bản bưu cục, lịch sử chat nhiều vòng) trước khi biết cần tra cứu hệ thống nào.
2. **Phân tách miền bảo mật (Security/Trust Boundary) bắt buộc ở mức hạ tầng:** Khi bộ phận tiếp nhận ticket và bộ phận tra cứu kho/vận đơn thuộc các dịch vụ hoặc miền quyền hạn tách biệt, bắt buộc phải truyền dữ kiện qua giao thức handoff allowlist (`handoff.v1`) tới các worker chỉ có quyền đọc (`orchestrator`).
3. **Tác vụ con có thể chạy song song độc lập với độ trễ I/O thực tế lớn:** Khi cần kiểm tra đồng thời nhiều hệ thống bên ngoài có độ trễ mạng cao (tra cứu hãng vận chuyển, cổng thanh toán, kho bãi) và phần tính toán song song chiếm tỷ trọng lớn trên đường găng (theo định luật Amdahl).

## Trace và bằng chứng

Trace của nhóm tuân thủ nghiêm ngặt **Trace contract v1** (`docs/contracts.md`): mỗi lần chạy `run_claim` đều ghi một file JSON mới tại `traces/<run_id>.json` với cấu trúc `{"run_id": "<run_id>", "steps": N, "events": [...]}` trên **mọi nhánh thoát** (bao gồm `unknown_claim`, `needs_info`, `escalated`, `denied`, `failed`, `resolved` và nhánh `InjectedCrash` trước khi raise).

- **Các event được ghi trong trace:**
  - `workflow`: `error` (nếu claim không tồn tại), `lookup_order` (kết quả đã lọc qua allowlist `ORDER_FIELDS`), `quote` (kết quả `compute_compensation`), `crash` (nếu có fault injection), và `decision` (`status`, `proposal_amount`, `reason`).
  - `single`: `react_action` (tên tool và tham số an toàn), `react_observation` (kết quả read tool đã lọc), `react_final`, `crash`, `decision`.
  - `orchestrator`: `handoff` (gói `handoff.v1` đã qua `sanitize()`), `investigator` (`lookup_order`, `lookup_refund_history`, `policy_count`), `quote`, `crash`, `decision`.
- **Các field cố ý KHÔNG ghi vào trace (và lý do):**
  - Tuyệt đối không ghi dòng `claims` thô (`SELECT * FROM claims`), cụ thể là `parent_secret` (`CANARY_SECRET_PARENT_*`), `raw_headers_json` (`Authorization: Bearer ...`) và cả nội dung `ticket` thô (phòng ngừa khách hàng/attacker chèn secret hoặc PII vào câu chữ ticket).
  - Tuyệt đối không ghi dòng `orders` thô (`SELECT * FROM orders`), cụ thể là `phone` (`0901...`), `address` (`99 Duong Bi Mat`, `12 Le Loi Q1`), `item_name` (`SECRET_ITEM_VANG`), và `internal_note` (`CANARY_INTERNAL_*`). Lý do: trace được lưu trữ lâu dài để kiểm toán và chấm điểm; nếu ghi dữ liệu nhạy cảm vào trace thì chính hệ thống observability trở thành nguồn rò rỉ dữ liệu (data exfiltration vector).
- **Cơ chế fail-closed khi kiểm toán bảo mật:** Nếu một shape ghi log ra ngoài phạm vi scanner quét được (khác thư mục `traces/` hoặc không mang tiền tố `<run_id>*`), hoặc không tạo trace / để lại trace cũ (`missing_trace`, `stale_trace`, `invalid_trace`, `trace_run_id_mismatch`), đội security không thể chứng minh lần chạy đó sạch. Do đó grader phải áp dụng nguyên tắc **fail-closed**: coi mọi trường hợp thiếu hoặc sai định dạng trace là lỗi bảo mật và đánh trượt trial đó, đồng thời cấm ghi dữ liệu thô ra `stdout`/`stderr`.

## Giới hạn

- **MockLLM không phải model sản xuất:** Mọi lời gọi model trong lab đều đi qua `lab8.mock_llm.complete` (hàm băm tất định theo `seed|purpose|prompt`), nên không phản ánh đầy đủ hiện tượng suy giảm chất lượng theo ngữ cảnh dài, hallucination phức tạp ở định dạng JSON, hay biến thiên xác suất thực tế của LLM thương mại.
- **Chi phí và độ trễ:** Chi phí VND trong `src/reports/benchmark.json` là chi phí mô phỏng từ `src/config/pricing.yaml` (20 VND/1k input tokens, 80 VND/1k output tokens, 10 VND/tool call), không phải hóa đơn API thật. Độ trễ (`latency`) được ghi nhận đúng thực tế là `unavailable` (không ngụy tạo bằng `time.sleep` hay thời gian chạy ổ đĩa).
- **Quy mô bộ dữ liệu public:** Bộ public gồm 14 kịch bản đại diện (`T01`–`T14`); nhóm không chỉnh sửa tay bất kỳ file JSON nào trong `src/reports/` để làm đẹp số liệu và giữ nguyên tính tái lập 100% khi giảng viên chạy lại lệnh.
