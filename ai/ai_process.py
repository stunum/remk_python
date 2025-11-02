import os
import sys
import cv2
import numpy as np
import platform

# 强制添加当前目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Current directory: {current_dir}")
print(f"Operating System: {platform.system()}")
print(f"Python Version: {sys.version_info.major}.{sys.version_info.minor}")

try:
    # 直接导入当前目录的模块（不要使用 from ai import）
    import rgb_image_generate
    print("✓ Successfully imported rgb_image_generate")
except ImportError as e:
    print(f"✗ Failed to import rgb_image_generate: {e}")
    print(f"  请确保:")
    if platform.system() == "Windows":
        print(f"  1. 存在 rgb_image_generate.pyd 文件")
        print(f"  2. Python 版本为 3.10")
        print(f"  3. 已安装 Visual C++ Redistributable")
    else:
        print(f"  1. 存在 rgb_image_generate.so 文件")
        print(f"  2. 动态库与系统架构匹配")
    sys.exit(1)

# 初始化模型
model_path = os.path.join(current_dir, "model.onnx")
if not os.path.exists(model_path):
    print(f"✗ Model file not found: {model_path}")
    sys.exit(1)

try:
    colorizer = rgb_image_generate.ColorizationModel(model_path)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    sys.exit(1)



def process_colorization(ir_path: str, green_path: str, save_path: str):
    """
    处理图像颜色化的核心函数
    """
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
    result_bytes, h1, w1 = colorizer.generate_bgr(r_channel_bytes, g_channel_bytes, h, w)
    
    # 将字节流转换为 NumPy 数组并保存
    image = np.frombuffer(result_bytes, dtype=np.uint8).reshape(h1, w1, 3)
    
    # 确保保存目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    cv2.imwrite(save_path, image)
    
    return save_path
