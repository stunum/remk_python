"""
AI 图像处理模块
提供眼底图像的彩色化处理功能
"""
from loguru_logging import log
from utils.path import resource_path
import os
import cv2
import numpy as np
try:
    from ai import rgb_image_generate
    colorizer = rgb_image_generate.ColorizationModel(model_path)
    log.info("AI 模块加载成功")
except ImportError as e:
    log.error(f"缺少必需的依赖: {e}")
    raise RuntimeError(f"缺少必需的依赖: {e}")

model_path= resource_path("ai/model.onnx")


def process_colorization(ir_path: str, green_path: str, save_path: str) -> str:
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
    result_bytes, h1, w1 =colorizer.generate_bgr(r_channel_bytes, g_channel_bytes, h, w)
    
    # 将字节流转换为 NumPy 数组并保存
    image = np.frombuffer(result_bytes, dtype=np.uint8).reshape(h1, w1, 3)
    
    # 确保保存目录存在
    save_dir = os.path.dirname(save_path)
    if save_dir:  # 如果有目录部分
        os.makedirs(save_dir, exist_ok=True)
    
    cv2.imwrite(save_path, image)
    
    return save_path
