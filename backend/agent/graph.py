"""
LangGraph 后端服务入口
将 MySQLAgentTools 暴露为兼容 LangGraph 协议的 Agent
"""
import sys
import os
from typing import List, Any

# ---------- 日志（最先初始化，方便排查后续问题）----------
from agent.logger_config import setup_logger
logger = setup_logger("texttosql.graph")

# ---------- 加载配置 ----------
from agent.config import settings

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from agent.MySQLAgentTools import MySQLAgentTools


# ============ 启动日志 ============
logger.info("=" * 60)
logger.info("🚀 Text-to-SQL Agent 正在启动...")
logger.info(f"MySQL  : {settings.mysql_user}@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}")
logger.info(f"LLM    : {settings.deepseek_model} @ {settings.deepseek_base_url}")
logger.info(f"编码    : PYTHONUTF8={os.getenv('PYTHONUTF8', '未设置')}")
logger.info("=" * 60)


# ============ 参数校验 ============
if not settings.mysql_password:
    logger.error("❌ MYSQL_PASSWORD 未设置，请检查 backend/.env")
    raise ValueError("MYSQL_PASSWORD 不能为空")

if not settings.deepseek_api_key:
    logger.error("❌ DEEPSEEK_API_KEY 未设置，请检查 backend/.env")
    raise ValueError("DEEPSEEK_API_KEY 不能为空")

logger.info("✅ 配置校验通过")


# ============ 1. 初始化数据库工具 ============
try:
    db_tools = MySQLAgentTools(
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        host=settings.mysql_host,
        port=settings.mysql_port,
        charset=settings.mysql_charset
    )
    logger.info("✅ MySQLAgentTools 初始化成功")
except Exception as e:
    logger.exception(f"❌ MySQLAgentTools 初始化失败: {e}")
    raise


# ============ 2. 初始化 LLM ============
try:
    llm = ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        streaming=True,
        temperature=0
    )
    logger.info("✅ DeepSeek LLM 初始化成功")
except Exception as e:
    logger.exception(f"❌ LLM 初始化失败: {e}")
    raise


# ============ 3. 获取工具列表 ============
try:
    tools: List[Any] = db_tools.get_tools()
    logger.info(f"✅ 已加载 {len(tools)} 个工具:")
    for t in tools:
        logger.info(f"   - {t.name}: {t.description[:50]}...")
except Exception as e:
    logger.exception(f"❌ 工具加载失败: {e}")
    raise


# ============ 4. 获取用户权限 ============
try:
    permission = db_tools.db.get_user_permissions()
    logger.info("✅ 已获取当前用户权限:")
    for line in permission.split("\n"):
        if line.strip():
            logger.info(f"   {line}")
except Exception as e:
    logger.warning(f"⚠️ 获取权限失败（不影响启动）: {e}")
    permission = "（权限信息获取失败）"


# ============ 5. 构造系统提示词 ============
system_prompt = f"""你是一个数据库助手，能够执行对指定表的增删改查操作。
当前用户权限:
{permission}

你可以参考之前的对话内容来回答当前问题。
执行 SQL 前，如果不确定表结构，请先使用 get_create_table 工具获取建表语句。
"""


# ============ 6. 创建 Agent ============
try:
    graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    logger.info("=" * 60)
    logger.info("🎉 Agent 创建成功，服务已就绪")
    logger.info("=" * 60)
except Exception as e:
    logger.exception(f"❌ Agent 创建失败: {e}")
    raise