"""
眼底图像保存API
从Go项目迁移的图像保存功能，适配ViewImages.vue页面
"""
import os
import base64
from datetime import datetime
import pathlib
from typing import List, Optional
from pathlib import Path
from PIL import Image
from io import BytesIO

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.fundus_image import FundusImage
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from utils.jwt_auth import get_current_user_id
from loguru_logging import log

# 导入 AI 处理函数，但允许导入失败
try:
    from ai.ai_process import process_colorization
except ImportError as e:
    log.warning(f"AI 模块导入失败: {e}")

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class SaveImageRequest(BaseModel):
    """保存单张图片请求模型（灰度模式）"""
    examination_id: int = PydanticField(..., gt=0, description="检查ID")
    file_dir: str = PydanticField(..., description="文件目录路径")
    image_name: str = PydanticField(..., description="图片文件名")
    eye_side: str = PydanticField(..., description="眼别：OD(右眼)/OS(左眼)")
    image_type: Optional[str] = PydanticField(None, description="图像类型")
    resolution: Optional[str] = PydanticField(None, description="分辨率")
    file_format: str = PydanticField(..., description="文件格式")
    acquisition_device: Optional[str] = PydanticField(None, description="采集设备")
    capture_mode: str = PydanticField(..., description="拍摄模式：gray/color")


class SaveMultiImageRequest(BaseModel):
    """保存多张图片请求模型（彩色模式）"""
    examination_id: int = PydanticField(..., gt=0, description="检查ID")
    file_dir: str = PydanticField(..., description="文件目录路径")
    image_name: List[str] = PydanticField(...,
                                          min_length=1, description="图片文件名列表")
    eye_side: str = PydanticField(..., description="眼别：OD(右眼)/OS(左眼)")
    image_type: Optional[str] = PydanticField(None, description="图像类型")
    resolution: Optional[str] = PydanticField(None, description="分辨率")
    file_format: str = PydanticField(..., description="文件格式")
    acquisition_device: Optional[str] = PydanticField(None, description="采集设备")
    capture_mode: str = PydanticField(..., description="拍摄模式：gray/color")


class HandeSaveImages(BaseModel):
    """手柄拍摄保存图片"""
    mode: str = PydanticField(..., description="拍摄模式：gray/color")
    eye_side: str = PydanticField(..., description="眼别：OD(右眼)/OS(左眼)")
    file: List[str] = PydanticField(..., min_length=1, description="图片文件名列表")
    file_format: str = PydanticField(..., description="文件格式")
    resolution: str = PydanticField(..., description="分辨率")
    examination_id:  int = PydanticField(..., gt=0, description="检查ID")

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "gray",
                "eye_side": "OD",
                "file": ["/Users/stunum/Downloads/00906241/PictureData/2025-06-19/145527_IR.jpg"],
                "file_format": "jpg",
                "resolution": "2048*2048",
                "examination_id": 12
            }
        }


class ImageInfo(BaseModel):
    """图片信息响应模型"""
    id: int = PydanticField(..., description="图片ID")
    image_path: str = PydanticField(..., description="图片路径")
    thumbnail_data: str = PydanticField(..., description="缩略图base64数据")


class ColorModeResponse(BaseModel):
    """彩色模式响应模型"""
    images: List[ImageInfo] = PydanticField(..., description="图片列表")
    capture_mode: str = PydanticField(..., description="拍摄模式")
    image_number: str = PydanticField(..., description="影像编号")


# ==================== 工具函数 ====================

def img_path_to_base64(img_path: str, quality: int = 40) -> str:
    """
    将图片路径转换为base64编码（压缩后）

    Args:
        img_path: 图片文件路径
        quality: JPEG压缩质量（1-100）

    Returns:
        str: base64编码的图片数据
    """
    try:
        # 打开图片
        with Image.open(img_path) as img:
            # 转换为RGB模式（如果是RGBA或其他模式）
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 压缩图片
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)

            # 转换为base64
            thumbnail_data = f"data:image/jpeg;base64,{base64.b64encode(buffer.read()).decode('utf-8')}"
            return thumbnail_data

    except Exception as e:
        log.error(f"转换图片为Base64失败: {img_path}, 错误: {str(e)}")
        raise ValueError(f"转换图片为Base64失败: {str(e)}")


def generate_image_number(examination_id: int) -> str:
    """
    生成影像编号
    格式: FIYYYYMMDDHHMMSS{examination_id}

    Args:
        examination_id: 检查ID

    Returns:
        str: 影像编号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"FI{timestamp}{examination_id}"


def generate_color_filename() -> str:
    """
    生成彩色图片文件名
    格式: HHMMSS_color.jpg

    Returns:
        str: 文件名
    """
    timestamp = datetime.now().strftime("%H%M%S")
    return f"{timestamp}_color.jpg"


def insert_fundus_image(
    session: Session,
    examination_id: int,
    image_number: str,
    eye_side: str,
    capture_mode: str,
    file_dir: str,
    image_name: str,
    file_size: int,
    file_format: str,
    thumbnail_data: str,
    user_id: int,
    image_type: Optional[str] = None,
    acquisition_device: Optional[str] = None,
    is_primary: bool = False
) -> int:
    """
    插入眼底图像记录到数据库

    Returns:
        int: 插入的记录ID
    """
    try:
        fundus_image = FundusImage(
            examination_id=examination_id,
            image_number=image_number,
            eye_side=eye_side,
            capture_mode=capture_mode,
            image_type=image_type,
            file_path=file_dir,
            file_name=image_name,
            file_size=file_size,
            file_format=file_format,
            acquisition_device=acquisition_device,
            upload_status="uploaded",
            thumbnail_data=thumbnail_data,
            is_primary=is_primary,
            created_by=user_id
        )

        session.add(fundus_image)
        session.commit()
        session.refresh(fundus_image)

        log.info(f"插入眼底图像记录成功: ID={fundus_image.id}, 编号={image_number}")
        return fundus_image.id

    except Exception as e:
        session.rollback()
        log.error(f"插入眼底图像记录失败: {str(e)}")
        raise


# ==================== API 端点 ====================

@router.post("/save-image", response_model=ResponseModel, summary="保存单张图片（灰度模式）")
async def save_image_to_local(
    request: SaveImageRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    保存单张眼底图片到本地并记录到数据库（灰度模式）

    - **examination_id**: 检查ID
    - **file_dir**: 图片文件目录
    - **image_name**: 图片文件名
    - **eye_side**: 眼别（OD/OS）
    - **file_format**: 文件格式
    - **capture_mode**: 拍摄模式（gray/color）
    """
    try:
        log.info(
            f"保存单张图片: examination_id={request.examination_id}, image_name={request.image_name}")

        # 生成影像编号
        image_number = generate_image_number(request.examination_id)

        # 构建完整文件路径
        full_path = pathlib.Path(request.image_name)

        # 检查文件是否存在
        if not full_path.exists():
            log.error(f"图片文件不存在: {full_path}")
            return error_response(msg=f"图片文件不存在: {full_path}", code=404)

        # 获取文件大小
        file_size = full_path.stat().st_size
        log.info(f"图片文件大小: {file_size} bytes")

        # 转换为Base64（压缩）
        thumbnail_data = img_path_to_base64(str(full_path))
        log.info(f"缩略图Base64长度: {len(thumbnail_data)}")

        # 插入数据库
        inserted_id = insert_fundus_image(
            session=session,
            examination_id=request.examination_id,
            image_number=image_number,
            eye_side=request.eye_side,
            capture_mode=request.capture_mode,
            file_dir=str(full_path.parent),
            image_name=full_path.name,
            file_size=file_size,
            file_format=request.file_format,
            thumbnail_data=thumbnail_data,
            user_id=user_id,
            image_type=request.image_type,
            acquisition_device=request.acquisition_device,
            is_primary=True
        )

        log.info(f"图片保存成功: ID={inserted_id}")

        return success_response(
            data={
                "id": inserted_id,
                "image_number": image_number,
                "image_path": full_path,
                "thumbnailData": thumbnail_data,
                "capture_mode": request.capture_mode
            },
            msg="图像保存成功"
        )

    except ValueError as e:
        log.error(f"参数错误: {str(e)}")
        return error_response(msg=str(e), code=400)
    except Exception as e:
        session.rollback()
        log.error(f"保存图片失败: {str(e)}")
        return error_response(msg=f"保存图像记录失败: {str(e)}", code=500)


@router.post("/save-multi-image", response_model=ResponseModel, summary="保存多张图片（彩色模式）")
async def save_multi_image_to_local(
    request: SaveMultiImageRequest,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    保存多张眼底图片到本地并调用AI合成彩色图像（彩色模式）

    - **examination_id**: 检查ID
    - **file_dir**: 图片文件目录
    - **image_name**: 图片文件名列表（包含 _IR.jpg, _G.jpg, _R.jpg, _B.jpg）
    - **eye_side**: 眼别（OD/OS）
    - **file_format**: 文件格式
    - **capture_mode**: 拍摄模式（gray/color）

    功能流程：
    1. 保存所有原始图片到数据库
    2. 调用AI合成API生成彩色图像
    3. 保存合成的彩色图像到数据库
    """
    try:
        log.info(
            f"保存多张图片: examination_id={request.examination_id}, 图片数量={len(request.image_name)}")

        # 生成影像编号
        image_number = generate_image_number(request.examination_id)

        # 初始化响应数据
        color_mode_response = {
            "capture_mode": request.capture_mode,
            "image_number": image_number,
            "images": []
        }

        # 保存所有原始图片并识别各个通道
        ir_img = None
        green_img = None
        red_img = None
        blue_img = None

        tmp_images_li = []

        for img_name in request.image_name:
            log.info(f"处理图片: {img_name}")

            # 识别图片类型
            if img_name.endswith("_G.jpg"):
                green_img = img_name
            elif img_name.endswith("_IR.jpg"):
                ir_img = img_name
            elif img_name.endswith("_R.jpg"):
                red_img = img_name
            elif img_name.endswith("_B.jpg"):
                blue_img = img_name

            # 构建完整文件路径
            full_path = pathlib.Path(img_name)

            # 检查文件是否存在
            if not full_path.exists():
                log.error(f"图片文件不存在: {full_path}")
                return error_response(msg=f"图片文件不存在: {full_path}", code=404)

            # 获取文件大小
            file_size = full_path.stat().st_size
            # 转换为Base64（压缩）
            thumbnail_data = img_path_to_base64(str(full_path))

            # 插入数据库
            inserted_id = insert_fundus_image(
                session=session,
                examination_id=request.examination_id,
                image_number=image_number,
                eye_side=request.eye_side,
                capture_mode=request.capture_mode,
                file_dir=str(full_path.parent),
                image_name=full_path.name,
                file_size=file_size,
                file_format=request.file_format,
                thumbnail_data=thumbnail_data,
                user_id=user_id,
                image_type=request.image_type,
                acquisition_device=request.acquisition_device
            )

            # 添加到响应列表
            tmp_images_li.append({
                "id": inserted_id,
                "image_path": full_path,
                "thumbnail_data": thumbnail_data,
                "eye_side":request.eye_side
            })

            log.info(f"图片保存成功: ID={inserted_id}, 文件={img_name}")

        # 打印识别的通道
        log.info(
            f"识别的通道: IR={ir_img}, Green={green_img}, Red={red_img}, Blue={blue_img}")

        # 调用AI合成彩色图像
        if ir_img and green_img:
            log.info("开始调用AI合成彩色图像...")

            # 生成彩色图像文件名和路径
            color_img_name = generate_color_filename()
            file_dir = pathlib.Path(ir_img).parent
            color_img_path = file_dir.joinpath(color_img_name)

            # 调用本地AI合成模块
            try:
                log.info(
                    f"开始AI合成彩色图像: ir={ir_img}, green={green_img}, save={color_img_path}")

                # 调用本地AI处理函数（只需要IR和Green通道）
                save_path = process_colorization(
                    ir_path=ir_img,
                    green_path=green_img,
                    save_path=str(color_img_path)
                )
                if save_path:
                    log.info(f"AI合成成功: {save_path}")
                else:
                    return error_response(msg="AI 模块处理错误！", code=400)
                # 获取彩色图像文件大小
                color_file_size = color_img_path.stat().st_size

                # 转换彩色图像为Base64
                color_thumbnail_data = img_path_to_base64(str(color_img_path))

                # 保存彩色图像到数据库
                color_inserted_id = insert_fundus_image(
                    session=session,
                    examination_id=request.examination_id,
                    image_number=image_number,
                    eye_side=request.eye_side,
                    capture_mode=request.capture_mode,
                    file_dir=str(color_img_path.parent),
                    image_name=color_img_path.name,
                    file_size=color_file_size,
                    file_format=request.file_format,
                    thumbnail_data=color_thumbnail_data,
                    user_id=user_id,
                    image_type=request.image_type,
                    acquisition_device=request.acquisition_device,
                    is_primary=True
                )

                # 添加彩色图像到响应列表
                color_mode_response["images"].append({
                    "id": color_inserted_id,
                    "image_path": save_path,
                    "thumbnail_data": color_thumbnail_data,
                    "eye_side":request.eye_side
                })
                color_mode_response["images"].extend(tmp_images_li)
                log.info(f"彩色图像保存成功: ID={color_inserted_id}")

            except Exception as e:
                log.error(f"AI合成失败: {str(e)}")
                # AI合成失败不影响原始图片的保存，继续返回成功
                log.warning("AI合成失败，但原始图片已保存")
        else:
            log.warning("未找到完整的四个通道图片，跳过AI合成")

        log.info(f"多张图片保存完成，总计: {len(color_mode_response['images'])} 张")

        return success_response(
            data=color_mode_response,
            msg="图像保存成功"
        )

    except ValueError as e:
        log.error(f"参数错误: {str(e)}")
        return error_response(msg=str(e), code=400)
    except Exception as e:
        session.rollback()
        log.error(f"保存多张图片失败: {str(e)}")
        return error_response(msg=f"保存图像记录失败: {str(e)}", code=500)


@router.post("hande/save-image", response_model=ResponseModel, summary="保存多张图片（彩色模式）")
async def hande_save_image(
    request: HandeSaveImages,
    session: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    log.info(f"request={request}")
    # 生成影像编号
    image_number = generate_image_number(request.examination_id)
    if request.mode == "gray":
        # 单摄
        try:
            # 构建完整文件路径
            full_path = pathlib.Path(request.file[0])
            # 检查文件是否存在
            if not full_path.exists():
                log.error(f"图片文件不存在: {full_path}")
                return error_response(msg=f"图片文件不存在: {full_path}", code=404)
            # 获取文件大小
            file_size = full_path.stat().st_size
            log.info(f"图片文件大小: {file_size} bytes")
            # 转换为Base64（压缩）
            thumbnail_data = img_path_to_base64(str(full_path))
            log.info(f"缩略图Base64长度: {len(thumbnail_data)}")
            # 插入数据库
            inserted_id = insert_fundus_image(
                session=session,
                examination_id=request.examination_id,
                image_number=image_number,
                eye_side=request.eye_side,
                capture_mode=request.mode,
                file_dir=str(full_path.parent),
                image_name=full_path.name,
                file_size=file_size,
                file_format=request.file_format,
                thumbnail_data=thumbnail_data,
                user_id=user_id,
                is_primary=True
            )

            log.info(f"图片保存成功: ID={inserted_id}")
            return success_response(
                data={
                    "id": inserted_id,
                    "image_number": image_number,
                    "image_path": full_path,
                    "thumbnailData": thumbnail_data,
                    "capture_mode": request.mode
                },
                msg="图像保存成功"
            )
        except ValueError as e:
            log.error(f"参数错误: {str(e)}")
            return error_response(msg=str(e), code=400)
        except Exception as e:
            session.rollback()
            log.error(f"保存图片失败: {str(e)}")
            return error_response(msg=f"保存图像记录失败: {str(e)}", code=500)
    else:
        # 多摄
        try:
            log.info(
                f"保存多张图片: examination_id={request.examination_id}, 图片数量={len(request.file)}")
            # 初始化响应数据
            color_mode_response = {
                "capture_mode": request.mode,
                "image_number": image_number,
                "images": []
            }
            # 保存所有原始图片并识别各个通道
            ir_img = None
            green_img = None
            red_img = None
            blue_img = None

            tmp_images_li = []
            for img_name in request.file:
                log.info(f"处理图片: {img_name}")

                # 识别图片类型
                if img_name.endswith("_G.jpg"):
                    green_img = img_name
                elif img_name.endswith("_IR.jpg"):
                    ir_img = img_name
                elif img_name.endswith("_R.jpg"):
                    red_img = img_name
                elif img_name.endswith("_B.jpg"):
                    blue_img = img_name

                # 构建完整文件路径
                full_path = pathlib.Path(img_name)
                # 检查文件是否存在
                if not full_path.exists():
                    log.error(f"图片文件不存在: {full_path}")
                    return error_response(msg=f"图片文件不存在: {full_path}", code=404)

                # 获取文件大小
                file_size = full_path.stat().st_size
                # 转换为Base64（压缩）
                thumbnail_data = img_path_to_base64(str(full_path))

                # 插入数据库
                inserted_id = insert_fundus_image(
                    session=session,
                    examination_id=request.examination_id,
                    image_number=image_number,
                    eye_side=request.eye_side,
                    capture_mode=request.mode,
                    file_dir=str(full_path.parent),
                    image_name=full_path.name,
                    file_size=file_size,
                    file_format=request.file_format,
                    thumbnail_data=thumbnail_data,
                    user_id=user_id
                )

                # 添加到响应列表
                tmp_images_li.append({
                    "id": inserted_id,
                    "image_path": full_path,
                    "thumbnail_data": thumbnail_data
                })

                log.info(f"图片保存成功: ID={inserted_id}, 文件={img_name}")
            # 打印识别的通道
            log.info(
                f"识别的通道: IR={ir_img}, Green={green_img}, Red={red_img}, Blue={blue_img}")
            # 调用AI合成彩色图像
            if ir_img and green_img:
                log.info("开始调用AI合成彩色图像...")

                # 生成彩色图像文件名和路径
                color_img_name = generate_color_filename()
                file_dir = pathlib.Path(ir_img).parent
                color_img_path = file_dir.joinpath(color_img_name)

                # 调用本地AI合成模块
                try:
                    log.info(
                        f"开始AI合成彩色图像: ir={ir_img}, green={green_img}, save={color_img_path}")

                    # 调用本地AI处理函数（只需要IR和Green通道）
                    save_path = process_colorization(
                        ir_path=ir_img,
                        green_path=green_img,
                        save_path=str(color_img_path)
                    )
                    if save_path:
                        log.info(f"AI合成成功: {save_path}")
                    else:
                        return error_response(msg="AI 模块处理错误！", code=400)
                    # 获取彩色图像文件大小
                    color_file_size = color_img_path.stat().st_size

                    # 转换彩色图像为Base64
                    color_thumbnail_data = img_path_to_base64(
                        str(color_img_path))

                    # 保存彩色图像到数据库
                    color_inserted_id = insert_fundus_image(
                        session=session,
                        examination_id=request.examination_id,
                        image_number=image_number,
                        eye_side=request.eye_side,
                        capture_mode=request.mode,
                        file_dir=str(color_img_path.parent),
                        image_name=color_img_path.name,
                        file_size=color_file_size,
                        file_format=request.file_format,
                        thumbnail_data=color_thumbnail_data,
                        user_id=user_id,
                        is_primary=True
                    )

                    # 添加彩色图像到响应列表
                    color_mode_response["images"].append({
                        "id": color_inserted_id,
                        "image_path": save_path,
                        "thumbnail_data": color_thumbnail_data
                    })
                    color_mode_response["images"].extend(tmp_images_li)
                    log.info(f"彩色图像保存成功: ID={color_inserted_id}")

                except Exception as e:
                    log.error(f"AI合成失败: {str(e)}")
                    # AI合成失败不影响原始图片的保存，继续返回成功
                    log.warning("AI合成失败，但原始图片已保存")
            else:
                log.warning("未找到完整的四个通道图片，跳过AI合成")

            log.info(f"多张图片保存完成，总计: {len(color_mode_response['images'])} 张")

            return success_response(
                data=color_mode_response,
                msg="图像保存成功"
            )

        except ValueError as e:
            log.error(f"参数错误: {str(e)}")
            return error_response(msg=str(e), code=400)
        except Exception as e:
            session.rollback()
            log.error(f"保存多张图片失败: {str(e)}")
            return error_response(msg=f"保存图像记录失败: {str(e)}", code=500)
