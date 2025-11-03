"""
眼科检查系统后端服务器启动入口
"""
import contextlib
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config
from database import db
from interface import api_router
from loguru_logging import log  # 导入全局日志对象


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    log.info("服务器启动中...")
    
    # 检查 AI 模块状态
    try:
        from ai.ai_process import is_ai_available, get_ai_error
        if is_ai_available():
            log.info("✓ AI 模块已加载，彩色图像合成功能可用")
        else:
            error_msg = get_ai_error()
            log.warning("✗ AI 模块不可用，彩色图像合成功能将不可用")
            log.warning(f"原因: {error_msg}")
    except Exception as e:
        log.warning(f"✗ AI 模块检查失败: {e}")
        log.warning("彩色图像合成功能将不可用，但其他功能正常")
    
    # 可以在这里添加其他启动时需要执行的操作
    yield
    # 关闭事件
    log.info("服务器关闭中...")
    # 可以在这里添加其他关闭时需要执行的操作


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    # 创建FastAPI应用
    app = FastAPI(
        title="眼科检查系统API",
        description="眼科检查系统后端API服务",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该限制为特定域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册API路由
    app.include_router(api_router, prefix="/api")
    
    # 添加全局异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        log.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        log.exception(f"服务器内部错误: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"服务器内部错误: {str(exc)}"},
        )
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        log.debug("健康检查请求")
        
        # 检查 AI 模块状态
        ai_status = {"available": False, "message": "未检查"}
        try:
            from ai.ai_process import is_ai_available, get_ai_error
            if is_ai_available():
                ai_status = {"available": True, "message": "AI 模块正常"}
            else:
                ai_status = {"available": False, "message": get_ai_error() or "加载失败"}
        except Exception as e:
            ai_status = {"available": False, "message": f"检查失败: {str(e)}"}
        
        return {
            "status": "ok",
            "ai_module": ai_status
        }
    
    return app


# 创建应用实例（模块级别），供uvicorn直接使用
app = create_app()


def main():
    """主函数，启动FastAPI服务器"""
    try:
        # 记录启动日志
        log.info("正在初始化眼科检查系统后端服务...")
        
        # 获取服务器配置
        server_config = config.config.server
        log.info(f"服务器配置: host={server_config.host}, port={server_config.port}")
        
        # 启动服务器
        log.info(f"启动服务器: http://{server_config.host}:{server_config.port}")
        uvicorn.run(
            "main:app",  # 使用字符串引用，避免重复创建app实例
            host=server_config.host,
            port=server_config.port,
            log_level="info",
            reload=True  # 开发模式下启用热重载
        )
    except Exception as e:
        log.exception(f"服务器启动失败: {str(e)}")
        raise


if __name__ == "__main__":
    main()
