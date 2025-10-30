"""
眼科检查系统后端服务器启动入口
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config
from database import db
from interface import api_router


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    # 创建FastAPI应用
    app = FastAPI(
        title="眼科检查系统API",
        description="眼科检查系统后端API服务",
        version="1.0.0"
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
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": f"服务器内部错误: {str(exc)}"},
        )
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    return app


def main():
    """主函数，启动FastAPI服务器"""
    # 获取服务器配置
    server_config = config.config.server
    
    # 创建FastAPI应用
    app = create_app()
    
    # 启动服务器
    uvicorn.run(
        app,
        host=server_config.host,
        port=server_config.port,
        log_level="info"
    )


if __name__ == "__main__":
    main()
