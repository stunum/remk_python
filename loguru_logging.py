"""
全局日志记录模块 - 使用loguru库
从config.yaml中获取配置，在项目启动时初始化
"""
import os
import sys
from pathlib import Path

from loguru import logger

from config import config, ConfigError


class LoggingConfig:
    """日志配置类"""
    
    @staticmethod
    def setup_logger():
        """
        设置全局logger
        从config.yaml中获取配置
        """
        try:
            # 获取日志配置
            log_config = config.config.logging
            
            # 移除默认的处理器
            logger.remove()
            
            # 设置日志格式
            log_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
            
            if log_config.format.lower() == "json":
                log_format = "{\"time\": \"{time:YYYY-MM-DD HH:mm:ss.SSS}\", \"level\": \"{level}\", \"name\": \"{name}\", \"function\": \"{function}\", \"line\": \"{line}\", \"message\": \"{message}\"}"
            
            # 设置日志级别
            log_level = log_config.level.upper()
            
            # 设置日志输出
            if log_config.output.lower() == "stdout":
                # 输出到控制台
                logger.add(
                    sys.stdout,
                    format=log_format,
                    level=log_level,
                    diagnose=True,
                    backtrace=True
                )
            else:
                # 输出到文件
                log_file_path = log_config.file_path
                
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file_path)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                # 添加文件处理器
                logger.add(
                    log_file_path,
                    format=log_format,
                    level=log_level,
                    rotation=log_config.rotation,  # 日志文件轮转大小
                    retention=log_config.retention,  # 日志保留时间
                    compression=log_config.compression,  # 压缩方式
                    diagnose=True,  # 显示诊断信息
                    backtrace=True,  # 显示回溯信息
                    enqueue=True  # 多进程安全
                )
            
            # 配置是否显示调用者信息
            logger.configure(extra={"report_caller": log_config.report_caller})
            
            logger.info("日志系统初始化完成")
            return logger
            
        except (ConfigError, Exception) as e:
            # 如果配置读取失败，使用默认配置
            logger.remove()
            logger.add(
                sys.stderr,
                format="<red>[ERROR]</red> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
                level="DEBUG",
                diagnose=True
            )
            logger.error(f"日志系统初始化失败，使用默认配置: {str(e)}")
            return logger


# 初始化全局logger
log = LoggingConfig.setup_logger()


# 使用示例
if __name__ == "__main__":
    log.debug("这是一条调试日志")
    log.info("这是一条信息日志")
    log.warning("这是一条警告日志")
    log.error("这是一条错误日志")
    log.critical("这是一条严重错误日志")
    
    # 带结构化数据的日志
    log.info("用户登录", extra={"user_id": 123, "username": "admin"})
    
    # 异常日志
    try:
        1 / 0
    except Exception as e:
        log.exception(f"发生异常: {str(e)}")