"""
AI 模块初始化
处理跨平台的扩展模块导入，在 Windows 下如果 DLL 加载失败则提供友好提示
"""
import os
import sys
import platform
from typing import Optional

# AI 模块可用性标记
AI_MODULE_AVAILABLE = False
AI_MODULE_ERROR: Optional[str] = None

def _check_ai_modules():
    """检查 AI 模块是否可用"""
    global AI_MODULE_AVAILABLE, AI_MODULE_ERROR
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查必需的文件是否存在
    if platform.system() == "Windows":
        required_file = os.path.join(current_dir, "rgb_image_generate.pyd")
    else:
        required_file = os.path.join(current_dir, "rgb_image_generate.so")
    
    if not os.path.exists(required_file):
        AI_MODULE_ERROR = f"AI 扩展模块文件不存在: {required_file}"
        return False
    
    # 尝试导入
    try:
        # 临时添加当前目录到路径
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        import rgb_image_generate  # noqa: F401
        AI_MODULE_AVAILABLE = True
        return True
        
    except ImportError as e:
        error_msg = str(e)
        
        if platform.system() == "Windows":
            AI_MODULE_ERROR = (
                f"AI 模块导入失败 (Windows DLL 问题): {error_msg}\n\n"
                "可能的解决方案:\n"
                "1. 确保使用 Python 3.10 (检查: python --version)\n"
                "2. 安装 Visual C++ Redistributable 2015-2022:\n"
                "   下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
                "3. 重新安装依赖: pip install -r requirements.txt\n"
                "4. 查看详细文档: WINDOWS_DLL_FIX.md\n"
                "5. 运行诊断工具: python check_environment.py"
            )
        else:
            AI_MODULE_ERROR = (
                f"AI 模块导入失败: {error_msg}\n\n"
                "可能的解决方案:\n"
                "1. 检查动态库依赖: ldd {required_file}\n"
                "2. 确保所有依赖已安装: pip install -r requirements.txt"
            )
        
        return False
    
    except Exception as e:
        AI_MODULE_ERROR = f"AI 模块加载时发生未预期的错误: {type(e).__name__}: {str(e)}"
        return False

# 在模块导入时检查
_check_ai_modules()

# 导出标记
__all__ = ['AI_MODULE_AVAILABLE', 'AI_MODULE_ERROR']

