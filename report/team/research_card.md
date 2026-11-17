# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu                         | Nguồn (thư viện tham khảo, slide 68–69)                            | Câu hỏi gợi ý cho lab                                                                                                        |
| --------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| R1 · Scaling                | Google Research 2026, _Towards a Science of Scaling Agent Systems_ | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy       | MAST, NeurIPS 2025, _Why Do Multi-Agent LLM Systems Fail?_         | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng?                         |
| R3 · Architecture choices   | AgentArch, AACL 2026                                               | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng?                                     |
| R4 · Evaluation confounders | EMNLP 2026, _Rethinking Evaluation of MAS Efficiency_              | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed?                              |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field            | Hướng dẫn                                                                                         | Nhóm điền |
| ---------------- | ------------------------------------------------------------------------------------------------- | --------- |
| CÂU              | R1 / R2 / R3 / R4                                                                                 | R2 |
| SOURCE           | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm)            | MAST (NeurIPS 2025), "Why Do Multi-Agent LLM Systems Fail?", benchmark & taxonomy analysis |
| CLAIM            | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper                                     | Hệ thống multi-agent thường gặp lỗi kiểm chứng (verification failure) và khuếch đại nhiễu từ bối cảnh phi cấu trúc khi thiếu chốt chặn code-level. |
| BOUNDARY         | Model / dataset / setup giới hạn kết luận đó                                                      | Thực nghiệm trên bài toán xử lý claim LogiX-VN với MockLLM, seed 11-55, 14 claims public và bảng giá pricing.yaml. |
| HYPOTHESIS       | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Swarm sang Single ReAct Agent có giới hạn đọc nghiêm ngặt (worker=True), lỗi tin lời ticket ở seed 55 giảm về 0, pass rate đạt 1.000, variance giảm về 0.0. |
| METHOD           | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: …      | Cố định: MockLLM, công cụ đọc, 14 claims public, 5 seeds (11, 22, 33, 44, 55), host evaluator. Biến thay đổi duy nhất: Topology (Swarm phi cấu trúc -> Single ReAct Agent). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass            | Đo bằng pass rate (mong đợi 1.0 vs 0.985 của swarm), pass^5 (1.0 vs 0.928), seed variance (0.0 vs 0.0002), và cost per success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - **Đúng như hypothesis**: Shape B (`single`) đạt pass rate = 1.000 (70/70 trial pass), pass^5 = 1.000, seed variance = 0.000.
  - Ngược lại, Shape D (`swarm`) bị thất bại ở seed 55 trên claim C-002 do cơ chế `model_override` tin số ngày trễ ghi trong ticket thay vì kiểm chứng từ cơ sở dữ liệu, dẫn đến pass rate chỉ đạt 0.985, pass^5 = 0.928.
  - Chi phí `single` (39.15 VND/success) tối ưu hơn nhiều so với `swarm` do loại bỏ các cuộc đối thoại peer-to-peer không kiểm soát.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
