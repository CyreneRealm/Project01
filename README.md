# Pipeline Thu Thập Dữ Liệu Thời Tiết Tự Động (ETL)

Hệ thống ETL được đóng gói bằng Docker, tự động trích xuất dữ liệu thời tiết Hà Nội từ OpenWeatherMap API, xử lý/biến đổi dữ liệu và tải vào cơ sở dữ liệu PostgreSQL. Quy trình được lập lịch và điều phối tự động mỗi giờ một lần thông qua Apache Airflow.

---

## Tính Năng Nổi Bật
- **Trích xuất dữ liệu (Data Extraction)**: Tự động gọi REST API bằng thư viện `requests` của Python.
- **Điều phối quy trình (Workflow Orchestration)**: Lập lịch chạy mỗi giờ bằng Apache Airflow DAGs với cấu hình tự động thử lại khi lỗi (retries) và quản lý lỗi hiệu quả.
- **Lưu trữ tối ưu (Idempotent Storage)**: Thiết kế bảng PostgreSQL với tính năng `UPSERT` (`ON CONFLICT DO NOTHING` trên cặp khóa duy nhất `city` + `observation_time`) nhằm ngăn chặn việc ghi trùng lặp dữ liệu lịch sử.
- **Đóng gói hệ thống (Containerization)**: Sử dụng Docker và Docker Compose để thiết lập môi trường chạy đa container độc lập, dễ dàng triển khai.

---

## Cấu Trúc Thư Mục
```text
.
├── dags/
│   ├── airlfow.py       # Định nghĩa & cấu hình Airflow DAG
│   ├── get_api.py       # Kết nối và lấy dữ liệu từ OpenWeatherMap API
│   └── table.py         # Kết nối database, tạo schema và xử lý nạp dữ liệu
├── airflow_init.sql     # Script khởi tạo cơ sở dữ liệu ban đầu
├── docker-compose.yml   # Cấu hình hệ thống đa container với Docker Compose
└── README.md            # Tài liệu hướng dẫn dự án
```

---

## Hướng Dẫn Cài Đặt & Cấu Hinh

### Yêu Cầu Hệ Thống
- Đã cài đặt Docker & Docker Compose.
- Có API Key từ dịch vụ [OpenWeatherMap](https://openweathermap.org/api).

### Cấu Hình
1. Mở file `dags/get_api.py` và thay thế giá trị `api_key` bằng mã API Key của bạn:
   ```python
   api_key = "MÃ_API_KEY_CỦA_BẠN"
   ```

2. (Tùy chọn) Kiểm tra cấu hình kết nối PostgreSQL trong file `docker-compose.yml`:
   - **Tài khoản (Database User)**: `postgres_user`
   - **Mật khẩu (Database Password)**: `postgres_password`
   - **Tên cơ sở dữ liệu (Database Name)**: `database01`
   - **Cổng kết nối ngoài (Exposed Port)**: `5433` (được ánh xạ từ cổng `5432` trong container)

---

## Khởi Chạy Dự Án

1. **Khởi chạy các container**:
   Mở terminal tại thư mục gốc của dự án và chạy lệnh sau:
   ```bash
   docker compose up -d
   ```
   Lệnh này sẽ tải các image cần thiết (PostgreSQL 16 Alpine, Apache Airflow 3.2.2) và chạy các container dưới nền.

2. **Truy cập giao diện Apache Airflow**:
   - Mở trình duyệt và truy cập: `http://localhost:8000`.
   - Mật khẩu đăng nhập sẽ được tự động tạo và lưu trữ trong file `passwords.json`.

3. **Kiểm tra dữ liệu đã nạp**:
   Để xác minh dữ liệu đã được ghi thành công vào PostgreSQL, truy cập vào bên trong container cơ sở dữ liệu:
   ```bash
   docker compose exec db psql -U postgres_user -d database01
   ```
   Chạy truy vấn SQL sau để kiểm tra:
   ```sql
   SELECT * FROM p1.raw_weather_data;
   ```

---

## Thiết Kế Cơ Sở Dữ Liệu (Database Schema)
Dữ liệu thời tiết được lưu vào schema `p1` trong cơ sở dữ liệu `database01`:

| Tên Cột | Kiểu Dữ Liệu | Ràng Buộc / Mô Tả |
|---|---|---|
| `id` | `SERIAL` | `PRIMARY KEY` |
| `city` | `TEXT` | Tên thành phố (ví dụ: Hanoi) |
| `temperature` | `FLOAT` | Nhiệt độ (độ C) |
| `weather_descriptions` | `TEXT` | Mô tả trạng thái thời tiết |
| `wind_speed` | `FLOAT` | Tốc độ gió (m/s) |
| `observation_time` | `TIMESTAMP` | Thời gian quan trắc thời tiết |
| `inserted_at` | `TIMESTAMP` | Thời điểm nạp dữ liệu vào DB (Mặc định: `NOW()`) |
| `utc_offset` | `TEXT` | Độ lệch múi giờ UTC (ví dụ: `+07:00`) |

*Lưu ý: Ràng buộc duy nhất `unique_city_time UNIQUE (city, observation_time)` giúp đảm bảo không có bản ghi trùng lặp cho cùng một thành phố tại cùng một thời điểm quan trắc.*
