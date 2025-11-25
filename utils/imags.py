import base64
from io import BytesIO
from PIL import Image
from loguru_logging import log

@log.catch
def compress_image_to_base64(
    input_path: str,
    max_width: int = 1080,
    quality: int = 70
) -> str:
    """
    同时按尺寸和质量压缩图片，并返回base64字符串
    """
    with Image.open(input_path) as img:
        # 1. 等比例缩放尺寸
        w, h = img.size
        if w > max_width:
            scale = max_width / w
            new_size = (max_width, int(h * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 2. 保存到内存 buffer，并压缩质量
        buffer = BytesIO()
        log.debug(f"img.format={img.format}")
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        buffer.seek(0)

        # 3. 转成 Base64
        b64_str = base64.b64encode(buffer.read()).decode("utf-8")
        return b64_str

@log.catch
def compress_to_dataurl(input_path: str,
                        max_width: int = 1080,
                        quality: int = 70):
    b64 = compress_image_to_base64(input_path, max_width, quality)
    return f"data:image/jpeg;base64,{b64}"
