# backend/test_env.py
import os
from dotenv import load_dotenv

# 指定 .env 路径
env_path = os.path.join(os.path.dirname(__file__), ".env")
print("ENV 路径:", env_path)
print("是否存在:", os.path.exists(env_path))

# 加载
load_dotenv(env_path)

# 读取关键变量
print("MYSQL_PASSWORD =", os.getenv("MYSQL_PASSWORD"))
print("DEEPSEEK_API_KEY =", os.getenv("DEEPSEEK_API_KEY"))