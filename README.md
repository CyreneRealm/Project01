# Weather ETL Pipeline

Pipeline ETL đóng gói bằng Docker, thu thập dữ liệu thời tiết Hà Nội từ OpenWeatherMap API, xử lý và nạp vào PostgreSQL. Điều phối tự động mỗi giờ bằng Apache Airflow.

## Tính năng
- **Extract**: Gọi REST API bằng thư viện `requests`
- **Orchestrate**: DAG Airflow chạy mỗi giờ, có retry và xử lý lỗi
- **Idempotent load**: `UPSERT` trên `(city, observation_time)` để tránh trùng lặp
- **Containerized**: Docker Compose, nhiều container

## Cấu trúc
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

## Cài đặt
1. Cần có Docker & Docker Compose, và [API key OpenWeatherMap](https://openweathermap.org/api).
2. Điền API key vào `dags/get_api.py` 
3. Chỉnh cấu hình PostgreSQL trong `docker-compose.yml` nếu cần.

## Chạy
```bash
docker compose up -d
```
Tải image PostgreSQL 16 Alpine + Airflow 3.2.2 và khởi chạy các container.

- Giao diện Airflow: `http://localhost:8000`
- Kiểm tra dữ liệu:
```bash
  docker compose exec db psql -U <POSTGRES_USER> -d <POSTGRES_DB>
```
```sql
  SELECT * FROM p1.raw_weather_data;
```

## Schema (`p1.raw_weather_data`)
| Cột | Kiểu | Mô tả |
|---|---|---|
| `id` | SERIAL | Khóa chính |
| `city` | TEXT | Tên thành phố |
| `temperature` | FLOAT | °C |
| `weather_descriptions` | TEXT | Mô tả thời tiết |
| `wind_speed` | FLOAT | m/s |
| `observation_time` | TIMESTAMP | Thời gian quan trắc |
| `inserted_at` | TIMESTAMP | Thời điểm nạp (mặc định `NOW()`) |
| `utc_offset` | TEXT | Lệch múi giờ UTC (vd `+07:00`) |
