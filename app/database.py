"""
Module cấu hình và khởi tạo kết nối Cơ sở dữ liệu sử dụng SQLAlchemy.
Hỗ trợ kết nối PostgreSQL hoặc SQLite (fallback).
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Database")

# Tải biến môi trường
load_dotenv()

# Đọc URL từ biến môi trường
POSTGRES_URL = os.getenv("POSTGRES_URL", "")
USE_SQLITE = os.getenv("USE_SQLITE", "True").lower() == "true"
SQLITE_PATH = os.getenv("SQLITE_PATH", "data/landslide.db")

# Logic quyết định sử dụng DB nào
if not USE_SQLITE and POSTGRES_URL:
    SQLALCHEMY_DATABASE_URL = POSTGRES_URL
    # Cấu hình Engine cho PostgreSQL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    logger.info("Đã cấu hình Engine kết nối đến PostgreSQL.")
else:
    # Đảm bảo thư mục SQLite tồn tại
    os.makedirs(os.path.dirname(SQLITE_PATH) if os.path.dirname(SQLITE_PATH) else ".", exist_ok=True)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    # Cấu hình Engine cho SQLite (check_same_thread=False cần thiết cho FastAPI)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    logger.info(f"Đã cấu hình Engine kết nối đến SQLite tại: {SQLITE_PATH}")

# Tạo factory class cho session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Lớp cơ sở (Base) cho tất cả các mô hình ORM (models) kế thừa
Base = declarative_base()

def get_db():
    """
    Dependency dùng để cung cấp Database Session cho các HTTP Route của FastAPI.
    Đảm bảo đóng Session an toàn sau khi req xử lý xong.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
