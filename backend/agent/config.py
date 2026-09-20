# backend/agent/config.py
import os
from pydantic_settings import BaseSettings

# # 计算 .env 的绝对路径：config.py 在 backend/agent/，.env 在 backend/
# ENV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# # 调试输出（首次运行时保留，确认路径正确后可以删除）
# print(f"[DEBUG] 期望加载的 .env 路径: {ENV_FILE}")
# print(f"[DEBUG] 文件是否存在: {os.path.exists(ENV_FILE)}")

class Settings(BaseSettings):
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = ""
    mysql_password: str = ""   # 必填
    mysql_database: str = "test_db_1"
    mysql_charset: str = "utf8mb4"

    deepseek_api_key: str = ""     # 必填
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

settings = Settings()