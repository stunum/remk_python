"""
AI 图像处理模块
提供眼底图像的彩色化处理功能
"""
import os
import sys
import platform
from typing import Optional, TYPE_CHECKING

# 延迟导入，避免在模块加载时就要求所有依赖
if TYPE_CHECKING:
    import cv2
    import numpy as np

# 延迟加载的全局变量
_colorizer: Optional[object] = None
_module_loaded: bool = False
_load_error: Optional[str] = None


def _lazy_load_model():
    """延迟加载 AI 模型，避免在模块导入时就失败"""
    global _colorizer, _module_loaded, _load_error
    
    # 如果已经尝试过加载（无论成功或失败），直接返回
    if _module_loaded:
        return _colorizer is not None
    
    _module_loaded = True
    
    try:
        # 强制添加当前目录到 Python 路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 尝试导入 rgb_image_generate
        import rgb_image_generate
        
        # 初始化模型
        model_path = os.path.join(current_dir, "model.onnx")
        if not os.path.exists(model_path):
            _load_error = f"模型文件不存在: {model_path}"
            return False
        
        _colorizer = rgb_image_generate.ColorizationModel(model_path)
        return True
        
    except ImportError as e:
        error_msg = str(e)
        if platform.system() == "Windows":
            _load_error = (
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
            _load_error = (
                f"AI 模块导入失败: {error_msg}\n"
                "请检查动态库依赖和 Python 包安装"
            )
        return False
        
    except Exception as e:
        _load_error = f"模型加载失败: {type(e).__name__}: {str(e)}"
        return False


def is_ai_available() -> bool:
    """检查 AI 模块是否可用"""
    return _lazy_load_model()


def get_ai_error() -> Optional[str]:
    """获取 AI 模块加载错误信息"""
    _lazy_load_model()  # 确保已经尝试加载
    return _load_error



def process_colorization(ir_path: str, green_path: str, save_path: str) -> str:
    """
    处理图像颜色化的核心函数
    
    Args:
        ir_path: 红外图像路径
        green_path: 绿色通道图像路径
        save_path: 输出图像保存路径
        
    Returns:
        str: 保存的图像路径
        
    Raises:
        RuntimeError: AI 模块不可用
        ValueError: 图像读取失败
        Exception: 其他处理错误
    """
    # 首先检查 AI 模块是否可用
    if not _lazy_load_model():
        error_msg = _load_error or "AI 模块加载失败，原因未知"
        raise RuntimeError(f"AI 模块不可用: {error_msg}")
    
    # 延迟导入 cv2 和 numpy
    try:
        import cv2
        import numpy as np
    except ImportError as e:
        raise RuntimeError(f"缺少必需的依赖: {e}")
    
    # 读取图像
    r_channel = cv2.imread(ir_path, 0)  # 0 表示灰度模式
    g_channel = cv2.imread(green_path, 0)
    
    if r_channel is None:
        raise ValueError(f"无法读取红外图像: {ir_path}")
    if g_channel is None:
        raise ValueError(f"无法读取绿色通道图像: {green_path}")
    
    h = r_channel.shape[0]
    w = r_channel.shape[1]
    
    # 转换为字节流
    g_channel_bytes = g_channel.tobytes()
    r_channel_bytes = r_channel.tobytes()
    
    # 调用颜色化模型
    result_bytes, h1, w1 = _colorizer.generate_bgr(r_channel_bytes, g_channel_bytes, h, w)
    
    # 将字节流转换为 NumPy 数组并保存
    image = np.frombuffer(result_bytes, dtype=np.uint8).reshape(h1, w1, 3)
    
    # 确保保存目录存在
    save_dir = os.path.dirname(save_path)
    if save_dir:  # 如果有目录部分
        os.makedirs(save_dir, exist_ok=True)
    
    cv2.imwrite(save_path, image)
    
    return save_path
