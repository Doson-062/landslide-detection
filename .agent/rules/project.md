# Rules bắt buộc — Landslide Detection System

## Database
- Dùng SQLAlchemy ORM, KHÔNG viết SQL thuần
- Mọi thao tác DB phải dùng get_db() dependency injection
- Luôn đóng session sau khi dùng
- KHÔNG dùng InfluxDB, chỉ dùng PostgreSQL

## Code
- KHÔNG hardcode credentials, token, password — đọc từ .env
- Dùng logging module, KHÔNG dùng print
- Mọi function phải có docstring tiếng Việt
- Validate input bằng Pydantic schemas trước khi lưu DB

## API
- Route trả HTML dùng TemplateResponse
- Route trả data dùng JSONResponse
- KHÔNG dùng MQTT, simulator gọi REST API trực tiếp

## Git
- KHÔNG commit file .env
- Commit message tiếng Việt, rõ ràng
