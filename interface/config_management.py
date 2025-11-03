"""
配置管理接口模块
提供database、third_party、server、logging、save_folder_path配置的查询和更新接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional

from config import config, ConfigError
from utils.response import success_response, error_response
from utils.jwt_auth import get_current_user
from loguru_logging import log


router = APIRouter()


# ========== Pydantic 模型定义 ==========

class DatabaseConfigResponse(BaseModel):
    """数据库配置响应模型"""
    host: str
    port: int
    user: str
    password: str
    dbname: str
    sslmode: str
    timezone: str
    max_idle_conns: int
    max_open_conns: int
    conn_max_lifetime: int
    log_level: str


class DatabaseConfigUpdate(BaseModel):
    """数据库配置更新模型"""
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    user: Optional[str] = None
    password: Optional[str] = None
    dbname: Optional[str] = None
    sslmode: Optional[str] = None
    timezone: Optional[str] = None
    max_idle_conns: Optional[int] = Field(None, ge=1)
    max_open_conns: Optional[int] = Field(None, ge=1)
    conn_max_lifetime: Optional[int] = Field(None, ge=0)
    log_level: Optional[str] = None


class ThirdPartyConfigResponse(BaseModel):
    """第三方服务配置响应模型"""
    base_url: str
    port: int
    timeout: int
    retry_count: int


class ThirdPartyConfigUpdate(BaseModel):
    """第三方服务配置更新模型"""
    base_url: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    timeout: Optional[int] = Field(None, ge=1)
    retry_count: Optional[int] = Field(None, ge=0)


class ServerConfigResponse(BaseModel):
    """服务器配置响应模型"""
    host: str
    port: int


class ServerConfigUpdate(BaseModel):
    """服务器配置更新模型"""
    host: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)


class LoggingConfigResponse(BaseModel):
    """日志配置响应模型"""
    level: str
    format: str
    output: str
    file_path: str
    report_caller: bool
    rotation: str
    retention: str
    compression: str


class LoggingConfigUpdate(BaseModel):
    """日志配置更新模型"""
    level: Optional[str] = None
    format: Optional[str] = None
    output: Optional[str] = None
    file_path: Optional[str] = None
    report_caller: Optional[bool] = None
    rotation: Optional[str] = None
    retention: Optional[str] = None
    compression: Optional[str] = None


class SaveFolderPathResponse(BaseModel):
    """保存文件夹路径响应模型"""
    save_folder_path: str


class SaveFolderPathUpdate(BaseModel):
    """保存文件夹路径更新模型"""
    save_folder_path: str


# ========== 数据库配置接口 ==========

@router.get("/database", summary="获取数据库配置")
async def get_database_config(current_user: dict = Depends(get_current_user)):
    """
    获取当前数据库配置
    
    需要用户认证
    """
    try:
        db_config = config.config.database
        log.info(f"用户 {current_user.get('username')} 获取数据库配置")
        
        return success_response(data={
            "host": db_config.host,
            "port": db_config.port,
            "user": db_config.user,
            "password": db_config.password,
            "dbname": db_config.dbname,
            "sslmode": db_config.sslmode,
            "timezone": db_config.timezone,
            "max_idle_conns": db_config.max_idle_conns,
            "max_open_conns": db_config.max_open_conns,
            "conn_max_lifetime": db_config.conn_max_lifetime,
            "log_level": db_config.log_level
        })
    except Exception as e:
        log.error(f"获取数据库配置失败: {str(e)}")
        return error_response(msg=f"获取数据库配置失败: {str(e)}", code=500)


@router.put("/database", summary="更新数据库配置")
async def update_database_config(
    update_data: DatabaseConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新数据库配置
    
    只更新提供的字段，未提供的字段保持不变
    需要用户认证
    """
    try:
        db_config = config.config.database
        
        # 更新提供的字段
        if update_data.host is not None:
            db_config.host = update_data.host
        if update_data.port is not None:
            db_config.port = update_data.port
        if update_data.user is not None:
            db_config.user = update_data.user
        if update_data.password is not None:
            db_config.password = update_data.password
        if update_data.dbname is not None:
            db_config.dbname = update_data.dbname
        if update_data.sslmode is not None:
            db_config.sslmode = update_data.sslmode
        if update_data.timezone is not None:
            db_config.timezone = update_data.timezone
        if update_data.max_idle_conns is not None:
            db_config.max_idle_conns = update_data.max_idle_conns
        if update_data.max_open_conns is not None:
            db_config.max_open_conns = update_data.max_open_conns
        if update_data.conn_max_lifetime is not None:
            db_config.conn_max_lifetime = update_data.conn_max_lifetime
        if update_data.log_level is not None:
            db_config.log_level = update_data.log_level
        
        # 保存配置到文件
        config.save()
        
        log.info(f"用户 {current_user.get('username')} 更新了数据库配置")
        
        return success_response(msg="数据库配置更新成功")
    except ConfigError as e:
        log.error(f"更新数据库配置失败: {str(e)}")
        return error_response(msg=f"更新数据库配置失败: {str(e)}", code=500)
    except Exception as e:
        log.error(f"更新数据库配置失败: {str(e)}")
        return error_response(msg=f"更新数据库配置失败: {str(e)}", code=500)


# ========== 第三方服务配置接口 ==========

@router.get("/third-party", summary="获取第三方服务配置")
async def get_third_party_config(current_user: dict = Depends(get_current_user)):
    """
    获取当前第三方服务配置
    
    需要用户认证
    """
    try:
        tp_config = config.config.third_party
        log.info(f"用户 {current_user.get('username')} 获取第三方服务配置")
        
        return success_response(data={
            "base_url": tp_config.base_url,
            "port": tp_config.port,
            "timeout": tp_config.timeout,
            "retry_count": tp_config.retry_count
        })
    except Exception as e:
        log.error(f"获取第三方服务配置失败: {str(e)}")
        return error_response(msg=f"获取第三方服务配置失败: {str(e)}", code=500)


@router.put("/third-party", summary="更新第三方服务配置")
async def update_third_party_config(
    update_data: ThirdPartyConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新第三方服务配置
    
    只更新提供的字段，未提供的字段保持不变
    需要用户认证
    """
    try:
        tp_config = config.config.third_party
        
        # 更新提供的字段
        if update_data.base_url is not None:
            tp_config.base_url = update_data.base_url
        if update_data.port is not None:
            tp_config.port = update_data.port
        if update_data.timeout is not None:
            tp_config.timeout = update_data.timeout
        if update_data.retry_count is not None:
            tp_config.retry_count = update_data.retry_count
        
        # 保存配置到文件
        config.save()
        
        log.info(f"用户 {current_user.get('username')} 更新了第三方服务配置")
        
        return success_response(msg="第三方服务配置更新成功")
    except ConfigError as e:
        log.error(f"更新第三方服务配置失败: {str(e)}")
        return error_response(msg=f"更新第三方服务配置失败: {str(e)}", code=500)
    except Exception as e:
        log.error(f"更新第三方服务配置失败: {str(e)}")
        return error_response(msg=f"更新第三方服务配置失败: {str(e)}", code=500)


# ========== 服务器配置接口 ==========

@router.get("/server", summary="获取服务器配置")
async def get_server_config(current_user: dict = Depends(get_current_user)):
    """
    获取当前服务器配置
    
    需要用户认证
    """
    try:
        server_config = config.config.server
        log.info(f"用户 {current_user.get('username')} 获取服务器配置")
        
        return success_response(data={
            "host": server_config.host,
            "port": server_config.port
        })
    except Exception as e:
        log.error(f"获取服务器配置失败: {str(e)}")
        return error_response(msg=f"获取服务器配置失败: {str(e)}", code=500)


@router.put("/server", summary="更新服务器配置")
async def update_server_config(
    update_data: ServerConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新服务器配置
    
    只更新提供的字段，未提供的字段保持不变
    需要用户认证
    
    注意：更新服务器配置后需要重启服务才能生效
    """
    try:
        server_config = config.config.server
        
        # 更新提供的字段
        if update_data.host is not None:
            server_config.host = update_data.host
        if update_data.port is not None:
            server_config.port = update_data.port
        
        # 保存配置到文件
        config.save()
        
        log.info(f"用户 {current_user.get('username')} 更新了服务器配置")
        log.warning("服务器配置已更新，需要重启服务才能生效")
        
        return success_response(msg="服务器配置更新成功，需要重启服务才能生效")
    except ConfigError as e:
        log.error(f"更新服务器配置失败: {str(e)}")
        return error_response(msg=f"更新服务器配置失败: {str(e)}", code=500)
    except Exception as e:
        log.error(f"更新服务器配置失败: {str(e)}")
        return error_response(msg=f"更新服务器配置失败: {str(e)}", code=500)


# ========== 日志配置接口 ==========

@router.get("/logging", summary="获取日志配置")
async def get_logging_config(current_user: dict = Depends(get_current_user)):
    """
    获取当前日志配置
    
    需要用户认证
    """
    try:
        logging_config = config.config.logging
        log.info(f"用户 {current_user.get('username')} 获取日志配置")
        
        return success_response(data={
            "level": logging_config.level,
            "format": logging_config.format,
            "output": logging_config.output,
            "file_path": logging_config.file_path,
            "report_caller": logging_config.report_caller,
            "rotation": logging_config.rotation,
            "retention": logging_config.retention,
            "compression": logging_config.compression
        })
    except Exception as e:
        log.error(f"获取日志配置失败: {str(e)}")
        return error_response(msg=f"获取日志配置失败: {str(e)}", code=500)


@router.put("/logging", summary="更新日志配置")
async def update_logging_config(
    update_data: LoggingConfigUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新日志配置
    
    只更新提供的字段，未提供的字段保持不变
    需要用户认证
    
    注意：更新日志配置后需要重启服务才能生效
    """
    try:
        logging_config = config.config.logging
        
        # 更新提供的字段
        if update_data.level is not None:
            logging_config.level = update_data.level
        if update_data.format is not None:
            logging_config.format = update_data.format
        if update_data.output is not None:
            logging_config.output = update_data.output
        if update_data.file_path is not None:
            logging_config.file_path = update_data.file_path
        if update_data.report_caller is not None:
            logging_config.report_caller = update_data.report_caller
        if update_data.rotation is not None:
            logging_config.rotation = update_data.rotation
        if update_data.retention is not None:
            logging_config.retention = update_data.retention
        if update_data.compression is not None:
            logging_config.compression = update_data.compression
        
        # 保存配置到文件
        config.save()
        
        log.info(f"用户 {current_user.get('username')} 更新了日志配置")
        log.warning("日志配置已更新，需要重启服务才能生效")
        
        return success_response(msg="日志配置更新成功，需要重启服务才能生效")
    except ConfigError as e:
        log.error(f"更新日志配置失败: {str(e)}")
        return error_response(msg=f"更新日志配置失败: {str(e)}", code=500)
    except Exception as e:
        log.error(f"更新日志配置失败: {str(e)}")
        return error_response(msg=f"更新日志配置失败: {str(e)}", code=500)


# ========== 保存文件夹路径配置接口 ==========

@router.get("/save-folder-path", summary="获取保存文件夹路径配置")
async def get_save_folder_path(current_user: dict = Depends(get_current_user)):
    """
    获取当前保存文件夹路径配置
    
    需要用户认证
    """
    try:
        save_path = config.config.save_folder_path
        log.info(f"用户 {current_user.get('username')} 获取保存文件夹路径配置")
        
        return success_response(data={
            "save_folder_path": save_path
        })
    except Exception as e:
        log.error(f"获取保存文件夹路径配置失败: {str(e)}")
        return error_response(msg=f"获取保存文件夹路径配置失败: {str(e)}", code=500)


@router.put("/save-folder-path", summary="更新保存文件夹路径配置")
async def update_save_folder_path(
    update_data: SaveFolderPathUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新保存文件夹路径配置
    
    需要用户认证
    """
    try:
        # 更新保存文件夹路径
        config.config.save_folder_path = update_data.save_folder_path
        
        # 保存配置到文件
        config.save()
        
        log.info(f"用户 {current_user.get('username')} 更新了保存文件夹路径配置: {update_data.save_folder_path}")
        
        return success_response(msg="保存文件夹路径配置更新成功")
    except ConfigError as e:
        log.error(f"更新保存文件夹路径配置失败: {str(e)}")
        return error_response(msg=f"更新保存文件夹路径配置失败: {str(e)}", code=500)
    except Exception as e:
        log.error(f"更新保存文件夹路径配置失败: {str(e)}")
        return error_response(msg=f"更新保存文件夹路径配置失败: {str(e)}", code=500)

