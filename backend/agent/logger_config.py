"""
统一日志配置模块
- 控制台输出（Docker 可采集）
- 文件输出（本地开发可查看）
- 支持环境变量控制日志级别
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "texttosql") -> logging.Logger:
    """
    创建并配置 logger。
    用法：
        from agent.logger_config import setup_logger
        logger = setup_logger(__name__)
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志级别从环境变量读取，默认 INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. 控制台 Handler（Docker 通过 stdout 采集）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件 Handler（本地开发用，带轮转）
    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "agent.log"),
        maxBytes=10 * 1024 * 1024,   # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 防止日志向上传播导致重复输出
    logger.propagate = False

    return logger