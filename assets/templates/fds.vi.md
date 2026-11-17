---
title: "{Tính năng} — Đặc tả thiết kế chức năng"
doc_id: FDS-{DOMAIN}-001
version: 0.1
status: Draft
owner: "{Chủ sở hữu tài liệu}"
reviewers: ["{Reviewer 1}", "{Reviewer 2}"]
jira: "{EPIC-KEY}"
space: "{SPACE}"
labels: [fds, "{domain}"]
classification: Internal
updated: "{YYYY-MM-DD}"
---

{{meta}}

{{toc}}

## 1. Mục đích và phạm vi

Tài liệu này đặc tả hành vi chức năng của {Tính năng}. Đây là hợp đồng triển khai cho {service hoặc team}, nguồn tham chiếu cho thiết kế kiểm thử của QA và căn cứ cho đánh giá sẵn sàng vận hành.

:::info
**Cần quyết định trước {ngày}.** {Một câu nêu quyết định, người chịu trách nhiệm và Jira key theo dõi.}
:::

### 1.1 Trong phạm vi

| Năng lực | Bao gồm | Ghi chú |
|---|---|---|
| {Năng lực A} | Có | {Ranh giới hoặc ràng buộc} |
| {Năng lực B} | Có | {Ranh giới hoặc ràng buộc} |
| {Năng lực C} | Không | Ngoài phạm vi; xem 1.2 |

### 1.2 Ngoài phạm vi

| Năng lực bị loại trừ | Lý do | Đơn vị xử lý |
|---|---|---|
| {Năng lực X} | {Lý do loại trừ} | {Team, hệ thống hoặc tài liệu} |
| {Năng lực Y} | {Lý do loại trừ} | {Team, hệ thống hoặc tài liệu} |

## 2. Các bên liên quan

| Vai trò | Họ tên | Trách nhiệm | RACI |
|---|---|---|---|
| Product owner | {Tên} | Phạm vi, ưu tiên và nghiệm thu | A |
| Engineering lead | {Tên} | Thiết kế và triển khai | R |
| QA lead | {Tên} | Chiến lược kiểm thử và bằng chứng nghiệm thu | R |
| Security engineer | {Tên} | Đánh giá mối đe dọa và xử lý dữ liệu | C |
| SRE / Vận hành | {Tên} | Runbook, giám sát và rollback | C |
| Compliance / Pháp chế | {Tên} | Đánh giá tuân thủ | C |
| {Team phụ thuộc} | {Tên} | {Sở hữu interface} | I |

## 3. Giả định và ràng buộc

| ID | Loại | Nội dung | Ảnh hưởng nếu sai |
|---|---|---|---|
| ASM-001 | Giả định | {Điều thiết kế đang dựa vào} | {Ảnh hưởng thiết kế hoặc phạm vi} |
| ASM-002 | Giả định | {Điều thiết kế đang dựa vào} | {Ảnh hưởng thiết kế hoặc phạm vi} |
| CON-001 | Ràng buộc | {Ràng buộc kỹ thuật, pháp lý hoặc tiến độ} | {Điều phải thay đổi} |
| CON-002 | Ràng buộc | {Ràng buộc kỹ thuật, pháp lý hoặc tiến độ} | {Điều phải thay đổi} |

## 4. Yêu cầu chức năng

Bảng dưới đây là chỉ mục yêu cầu. Mỗi yêu cầu có một kết quả quan sát được, một mức ưu tiên và một issue nguồn. Hành vi chi tiết và trường hợp biên được mô tả ở mục 4.1.

| ID | Yêu cầu | Ưu tiên | Jira | Trạng thái |
|---|---|---|---|---|
| FR-001 | {Phát biểu ngắn, kiểm thử được} | Must | {{jira:KEY-1}} | {{status:grey\|Draft}} |
| FR-002 | {Phát biểu ngắn, kiểm thử được} | Should | {{jira:KEY-2}} | {{status:grey\|Draft}} |
| FR-003 | {Phát biểu ngắn, kiểm thử được} | Could | {{jira:KEY-3}} | {{status:grey\|Draft}} |

### 4.1 FR-001 — {Tên yêu cầu}

Hệ thống **phải** {hành vi quan sát được}. Quy tắc áp dụng cho {phạm vi}, được thực thi tại {tầng} và trả về {kết quả} trong {giới hạn thời gian}.

| Thuộc tính | Giá trị |
|---|---|
| Điều kiện kích hoạt | {Sự kiện, lịch hoặc hành động người dùng} |
| Đầu vào | {Trường dữ liệu, định dạng và quy tắc kiểm tra} |
| Đầu ra | {Response, thay đổi trạng thái hoặc event} |
| Điều kiện tiên quyết | {Trạng thái hoặc quyền bắt buộc} |
| Điều kiện sau | {Trạng thái được bảo đảm sau khi thành công} |
| Hành vi khi lỗi | {Mã lỗi, chính sách retry và thông báo người dùng} |

#### Trường hợp biên

| Trường hợp | Hành vi mong đợi | Mã lỗi |
|---|---|---|
| {Điều kiện biên} | {Hệ thống xử lý thế nào} | {CODE hoặc không có} |
| {Request trùng lặp} | {Kết quả idempotent} | {CODE hoặc không có} |
| {Dependency timeout} | {Hành vi fallback} | {CODE hoặc không có} |

### 4.2 FR-002 — {Tên yêu cầu}

Hệ thống **phải** {hành vi quan sát được}. {Chỉ bổ sung chi tiết mà bảng tổng hợp không thể diễn đạt; không lặp lại nội dung bảng.}

| Thuộc tính | Giá trị |
|---|---|
| Điều kiện kích hoạt | {Sự kiện, lịch hoặc hành động người dùng} |
| Đầu vào | {Trường dữ liệu, định dạng và quy tắc kiểm tra} |
| Đầu ra | {Response, thay đổi trạng thái hoặc event} |
| Điều kiện tiên quyết | {Trạng thái hoặc quyền bắt buộc} |
| Điều kiện sau | {Trạng thái được bảo đảm sau khi thành công} |
| Hành vi khi lỗi | {Mã lỗi, chính sách retry và thông báo người dùng} |

## 5. Yêu cầu phi chức năng

| ID | Nhóm | Mục tiêu | Cách đo | Jira |
|---|---|---|---|---|
| NFR-001 | Hiệu năng | p95 dưới 300 ms tại 500 request/giây | Load test staging, chạy 30 phút | {{jira:KEY-4}} |
| NFR-002 | Sẵn sàng | 99,95% availability theo tháng | Dashboard SLO, cửa sổ 28 ngày | {{jira:KEY-5}} |
| NFR-003 | Bảo mật | Mã hóa dữ liệu khi truyền và khi lưu trữ | TLS 1.2+, rà soát KMS key policy | {{jira:KEY-6}} |
| NFR-004 | Khả năng quan sát | Mọi lỗi phát sinh log có cấu trúc và metric | Rà soát log schema và test alert | {{jira:KEY-7}} |
| NFR-005 | Khả năng tiếp cận | WCAG 2.2 AA cho mọi màn hình mới | Audit Axe và test bàn phím thủ công | {{jira:KEY-8}} |

## 6. Quy tắc nghiệp vụ

| ID | Quy tắc | Nơi thực thi | Mã lỗi | Jira |
|---|---|---|---|---|
| {{anchor:br-001}} BR-001 | {Điều kiện nghiệp vụ phải đúng} | {Service, database hoặc policy engine} | {CODE} | {{jira:KEY-9}} |
| {{anchor:br-002}} BR-002 | {Điều kiện nghiệp vụ phải đúng} | {Service, database hoặc policy engine} | {CODE} | {{jira:KEY-10}} |
| BR-003 | {Điều kiện nghiệp vụ phải đúng} | {Service, database hoặc policy engine} | {CODE} | {{jira:KEY-11}} |

## 7. Mô hình dữ liệu

Mô hình dưới đây là chuẩn. Tên trường khớp với hợp đồng API tại mục 8.

| Entity | Mục đích | Thời gian lưu trữ | Chủ sở hữu |
|---|---|---|---|
| {Entity A} | {Đại diện cho điều gì} | {Thời gian lưu} | {Team} |
| {Entity B} | {Đại diện cho điều gì} | {Thời gian lưu} | {Team} |

### 7.1 {Entity A}

| Trường | Kiểu | Bắt buộc | Ràng buộc | Mô tả |
|---|---|---|---|---|
| `id` | string (UUID) | Có | Bất biến | Khóa chính |
| `status` | enum | Có | {VALUE_1}, {VALUE_2} | Trạng thái vòng đời |
| `amount` | decimal(18,2) | Có | Lớn hơn 0 | {Giá trị đại diện} |
| `created_at` | timestamp | Có | ISO 8601, UTC | Thời điểm tạo |
| `{field}` | {type} | {có/không} | {ràng buộc} | {mô tả} |

## 8. Tích hợp và hợp đồng API

| Bên gọi | Bên cung cấp | Giao thức | Mục đích | Chủ sở hữu |
|---|---|---|---|---|
| {Consumer} | {Provider} | REST / HTTPS | {Mục đích} | {Team} |

### 8.1 Endpoint

| Method | Path | Mục đích | Xác thực | Idempotency |
|---|---|---|---|---|
| POST | `/v1/{resource}` | {Tạo hoặc thực hiện hành động} | OAuth 2.0 client credentials | Header `Idempotency-Key` |
| GET | `/v1/{resource}/{id}` | {Đọc một tài nguyên} | OAuth 2.0 client credentials | An toàn, lặp lại được |
| PATCH | `/v1/{resource}/{id}` | {Cập nhật tài nguyên} | OAuth 2.0 client credentials | Last write wins với `If-Match` |

### 8.2 Xử lý lỗi

| Mã | HTTP | Ý nghĩa | Retry | Thông báo cho người dùng |
|---|---|---|---|---|
| `{CODE_1}` | 400 | {Dữ liệu không hợp lệ} | Không | {Thông báo hiển thị} |
| `{CODE_2}` | 409 | {Xung đột trạng thái} | Không | {Thông báo hiển thị} |
| `{CODE_3}` | 503 | {Dependency không khả dụng} | Có, backoff lũy thừa | {Thông báo hiển thị} |

:::note
Schema chuẩn được công bố trong tài liệu OpenAPI. Mục này giải thích hành vi, không sao chép lại schema.
:::

## 9. Luồng người dùng và ghi chú UX

1. Người dùng mở {màn hình} và chọn {điểm vào}.
2. Hệ thống kiểm tra {dữ liệu đầu vào} và hiển thị {tóm tắt}.
3. Người dùng xác nhận; hệ thống gọi {endpoint} và hiển thị {trạng thái tiến trình}.
4. Khi thành công, hệ thống hiển thị {xác nhận} và ghi {audit event}.
5. Khi thất bại, hệ thống giữ người dùng trên trang, hiển thị {thông báo} và gợi ý {hành động khôi phục}.

:::info
**Trạng thái rỗng, đang tải và lỗi là một phần của tiêu chí chấp nhận.** Không chỉ đặc tả luồng thành công.
:::

| Trạng thái | Trải nghiệm mong đợi | Tham chiếu copy |
|---|---|---|
| Đang tải | {Skeleton, spinner hoặc progress text} | {Copy ID hoặc link} |
| Rỗng | {Giải thích và hành động chính} | {Copy ID hoặc link} |
| Không có quyền | {Người dùng thấy gì và liên hệ ai} | {Copy ID hoặc link} |
| Dependency lỗi | {Hành vi retry và fallback} | {Copy ID hoặc link} |

## 10. Tiêu chí chấp nhận

| AC ID | Yêu cầu | Kịch bản | Given | When | Then |
|---|---|---|---|---|---|
| AC-001 | FR-001 | {Tên kịch bản} | {Điều kiện trước} | {Hành động} | {Kết quả quan sát được} |
| AC-002 | FR-001 | {Kịch bản biên} | {Điều kiện trước} | {Hành động} | {Kết quả quan sát được} |
| AC-003 | FR-002 | {Kịch bản lỗi} | {Điều kiện trước} | {Hành động} | {Mã lỗi và thông báo} |
| AC-004 | NFR-001 | {Kịch bản hiệu năng} | {Hồ sơ tải} | {Lưu lượng duy trì} | {Ngưỡng đạt} |
| AC-005 | FR-003 | {Tên kịch bản} | {Điều kiện trước} | {Hành động} | {Kết quả quan sát được} |

## 11. Rủi ro và câu hỏi mở

### 11.1 Rủi ro

| ID | Rủi ro | Khả năng | Ảnh hưởng | Giảm thiểu | Chủ sở hữu | Trạng thái |
|---|---|---|---|---|---|---|
| RSK-001 | {Điều gì có thể sai} | Trung bình | Cao | {Giảm thiểu hoặc phương án dự phòng} | {Owner} | {{status:yellow\|Open}} |
| RSK-002 | {Điều gì có thể sai} | Thấp | Trung bình | {Giảm thiểu hoặc phương án dự phòng} | {Owner} | {{status:grey\|Monitoring}} |

### 11.2 Câu hỏi mở

| ID | Câu hỏi | Chủ sở hữu | Cần trả lời trước | Trạng thái |
|---|---|---|---|---|
| OQ-001 | {Câu hỏi chặn thiết kế hoặc triển khai} | {Owner} | {Ngày} | {{status:red\|Open}} |
| OQ-002 | {Câu hỏi chặn thiết kế hoặc triển khai} | {Owner} | {Ngày} | {{status:green\|Resolved}} |

## 12. Lịch sử thay đổi

| Phiên bản | Ngày | Người cập nhật | Thay đổi | Jira |
|---|---|---|---|---|
| 0.1 | {YYYY-MM-DD} | {Owner} | Bản nháp đầu tiên | {{jira:EPIC-KEY}} |

## Phụ lục A. Thuật ngữ

| Thuật ngữ | Định nghĩa | Nguồn |
|---|---|---|
| {Thuật ngữ} | {Định nghĩa kỹ sư mới có thể hiểu} | {Glossary hoặc tiêu chuẩn} |
| {Thuật ngữ} | {Định nghĩa kỹ sư mới có thể hiểu} | {Glossary hoặc tiêu chuẩn} |

## Phụ lục B. Tài liệu tham khảo

| Nguồn | Liên kết | Vì sao quan trọng |
|---|---|---|
| Epic | {{jira:EPIC-KEY}} | Theo dõi phạm vi và tiến độ |
| Hợp đồng API | [OpenAPI specification]({URL}) | Schema request/response chuẩn |
| Thiết kế | [Figma flow]({URL}) | Hành vi và trạng thái màn hình |
| Runbook | [Operations runbook]({URL}) | Quy trình on-call và rollback |
