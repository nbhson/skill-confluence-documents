# Vietnamese–English Glossary for Confluence Documents

One concept, one term. This glossary fixes the Vietnamese wording used across FDS, API specifications, RFCs, runbooks and review records. When a page introduces a term for the first time, use the Vietnamese term and keep the English term in parentheses if engineers will search for it.

Rules:

- Keep Jira keys, HTTP methods, field names and header names in English.
- Keep ISO dates (`2026-11-17`) and numbers with a dot thousands separator (`50.000.000 VND`) consistent within a page.
- Do not translate a product name, macro name or API resource.
- If a term is missing here, add it in one place and use it everywhere; do not create a synonym.

## Document Types

| English | Vietnamese | Notes |
|---|---|---|
| Functional Design Specification (FDS) | Đặc tả thiết kế chức năng | The canonical requirements document |
| API Specification | Đặc tả API | Keep `API` untranslated |
| Request for Comments (RFC) | Đề xuất kỹ thuật (RFC) | A decision proposal, not a meeting |
| Runbook | Sổ tay vận hành | On-call procedure |
| Release Notes | Ghi chú phát hành | Customer- and support-facing |
| Postmortem | Phân tích sau sự cố | Blameless incident review |
| Architecture Decision Record (ADR) | Bản ghi quyết định kiến trúc | Durable decision + consequences |
| Document control | Kiểm soát tài liệu | The metadata block, not a section |
| Change log | Lịch sử thay đổi | Last numbered section |
| Appendix | Phụ lục | Lettered, not numbered |

## Requirements

| English | Vietnamese | Notes |
|---|---|---|
| Requirement | Yêu cầu | One observable outcome |
| Functional requirement (FR) | Yêu cầu chức năng (FR) | Keep the ID prefix |
| Non-functional requirement (NFR) | Yêu cầu phi chức năng (NFR) | Must be measurable |
| Business rule (BR) | Quy tắc nghiệp vụ (BR) | Enforcement point required |
| Acceptance criterion (AC) | Tiêu chí nghiệm thu (AC) | Given–When–Then |
| Scope | Phạm vi | In and out of scope |
| Assumption | Giả định | Must be validated |
| Constraint | Ràng buộc | Technical, legal or budgetary |
| Stakeholder | Các bên liên quan | Named roles, not departments only |
| Priority (MoSCoW) | Mức ưu tiên (MoSCoW) | Must / Should / Could / Won't |
| Traceability | Truy vết | FR → AC → Jira → evidence |
| Edge case | Trường hợp biên | Boundary and failure behaviour |
| Precondition | Điều kiện tiên quyết | Must be true before the flow |
| Postcondition | Điều kiện sau | Must be true after success |
| Out of scope | Ngoài phạm vi | Explicit exclusion |
| Open question | Câu hỏi mở | Owner + needed-by date |
| Risk | Rủi ro | Likelihood, impact, mitigation |
| Mitigation | Biện pháp giảm thiểu | Owner and trigger |
| Dependency | Phụ thuộc | Team, service or decision |

## Status and Governance

| English | Vietnamese | Notes |
|---|---|---|
| Draft | Bản nháp | Not reviewed |
| In Review | Đang xem xét | Reviewers assigned |
| Approved | Đã phê duyệt | Version-specific |
| Approved with conditions | Phê duyệt có điều kiện | Conditions have owners and dates |
| Rejected | Từ chối | Reason recorded |
| Deprecated | Ngừng sử dụng | Successor named |
| Superseded | Đã được thay thế | Read-only history |
| Owner | Chủ sở hữu | Accountable decision maker |
| Reviewer | Người xem xét | Advises; does not own the decision |
| Approver | Người phê duyệt | Named in the review record |
| Sign-off | Ký duyệt | Version + evidence |
| Finding | Phát hiện | ID, severity, owner, status |
| Blocking finding | Phát hiện chặn phê duyệt | Must close before approval |
| Review cadence | Chu kỳ xem xét | Six-month default |
| Next review date | Ngày xem xét tiếp theo | Expiry control |
| Audit trail | Dấu vết kiểm toán | Version history + change log |
| Classification | Mức phân loại | Internal, Confidential, Public |
| Separation of duties | Phân tách trách nhiệm | Author ≠ approver where required |

## API and Data

| English | Vietnamese | Notes |
|---|---|---|
| Endpoint | Điểm cuối (endpoint) | Keep `endpoint` for engineers |
| Request | Yêu cầu | HTTP request |
| Response | Phản hồi | HTTP response |
| Status code | Mã trạng thái | Numeric, always documented |
| Error code | Mã lỗi | Stable, machine-readable |
| Error envelope | Cấu trúc lỗi | Same shape for every error |
| Idempotency key | Khóa bất biến | Header name stays English |
| Idempotent | Bất biến theo khóa | Safe to retry with the same key |
| Pagination | Phân trang | Cursor preferred |
| Rate limit | Giới hạn tần suất | Requests per window |
| Retry-after | Thời gian chờ thử lại | Header and seconds |
| Backoff | Giãn cách thử lại | Exponential with jitter |
| Authentication | Xác thực | Who the caller is |
| Authorization | Phân quyền | What the caller may do |
| Scope | Phạm vi quyền | OAuth scope |
| Tenant | Đơn vị thuê | Isolation boundary |
| Payload | Dữ liệu gửi | Request or event body |
| Schema | Lược đồ dữ liệu | OpenAPI/JSON Schema |
| Breaking change | Thay đổi phá vỡ tương thích | Needs a major version |
| Additive change | Thay đổi bổ sung | Non-breaking |
| Deprecation | Ngừng hỗ trợ | Notice + sunset date |
| Migration | Di chuyển | Consumer action |
| Contract test | Kiểm thử hợp đồng | Page version ↔ CI run |
| Sandbox | Môi trường thử nghiệm | Not production |
| Monetary amount | Số tiền | State minor units and currency |
| UTC timestamp | Thời điểm UTC | ISO 8601 with `Z` |

## Architecture and Operations

| English | Vietnamese | Notes |
|---|---|---|
| Service | Dịch vụ | Owned component |
| Component | Thành phần | Deployable or logical unit |
| Interface | Giao diện tích hợp | API, event or file |
| Data flow | Luồng dữ liệu | Direction and protocol |
| Sequence diagram | Biểu đồ tuần tự | Interaction order |
| State machine | Máy trạng thái | States + transitions |
| Entity relationship | Quan hệ thực thể | Cardinality only |
| Failure mode | Chế độ lỗi | Timeout, retry, dead letter |
| Fallback | Phương án dự phòng | Degraded behaviour |
| Rollback | Hoàn tác | Trigger + command |
| Rollout | Triển khai dần | Phased release |
| Feature flag | Cờ tính năng | Default state documented |
| Incident | Sự cố | Severity + commander |
| Severity (SEV) | Mức độ nghiêm trọng (SEV) | SEV-1/2/3 definitions |
| Mitigation | Giảm thiểu tác động | Stop the bleeding first |
| Root cause | Nguyên nhân gốc | System condition, not a person |
| Contributing factor | Yếu tố góp phần | Technical/process/organisational |
| Action item | Hạng mục hành động | Owner, due date, Jira key |
| Detection gap | Khoảng trễ phát hiện | Time to detect |
| Runbook step | Bước vận hành | Numbered, verifiable |

## Writing and Accessibility

| English | Vietnamese | Notes |
|---|---|---|
| Plain language | Ngôn ngữ đơn giản | Short sentences, common words |
| Heading | Tiêu đề mục | Real heading level |
| Table header | Tiêu đề cột | `<th>`, never merged |
| Link text | Văn bản liên kết | Destination + purpose |
| Alt text | Văn bản thay thế | States the conclusion |
| Screen reader | Trình đọc màn hình | VoiceOver / NVDA |
| Keyboard navigation | Điều hướng bằng bàn phím | No pointer-only action |
| Focus | Tiêu điểm | Visible focus indicator |
| Contrast | Độ tương phản | 4.5:1 body text |
| Zoom | Phóng to | Test at 200% |
| Reflow | Dàn lại bố cục | No horizontal scroll for prose |
| Caption | Chú thích hình | Numbered takeaway |
| Glossary | Bảng thuật ngữ | One term per concept |
| Acronym | Từ viết tắt | Expand on first use |
| Diacritics | Dấu tiếng Việt | Never strip for ASCII |
| Sentence case | Viết hoa câu | Not Title Case |
| Version message | Thông điệp phiên bản | `v{n} — area: change` |
| Deprecation banner | Thông báo ngừng sử dụng | Reason + successor |

## Preferred Phrasing

| Avoid | Prefer | Why |
|---|---|---|
| `Yeu cau chuc nang` | `Yêu cầu chức năng` | Screen readers and search need diacritics |
| `Click here` / `Tại đây` | `[Xem chính sách hoàn tiền](...)` | Link text must name the destination |
| `Update` as a version message | `v1.1 — BR-004: thêm phê duyệt kép` | Audit trail must be specific |
| `Fast` / `Nhanh` | `p95 < 400 ms ở 300 rps` | NFRs need a measurement |
| `System error` | `REFUND_AMOUNT_EXCEEDED` + user action | Errors must be actionable |
| `Etc.` in a requirements table | Explicit row or `—` | Ambiguity cannot be tested |
| `Approved` without a version | `Approved — v1.1, 2026-11-17` | Approval is version-specific |
