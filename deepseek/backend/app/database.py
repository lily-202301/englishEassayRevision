from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 智能判断：如果有环境变量 DATABASE_URL 就用它（Docker里），否则用本地 SQLite
# 注意：SQLAlchemy 用 Postgres 需要写成 postgresql://，但环境变量有时候是 postgres://，这里做一个替换保险
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db").replace("postgres://", "postgresql://")

# 检查是否是 SQLite（SQLite 需要特殊参数 check_same_thread）
connect_args = {"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()