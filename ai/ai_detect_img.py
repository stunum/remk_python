import cv2
import onnxruntime as ort
from PIL import ImageFont, ImageDraw
import numpy as np
from PIL import Image
import pathlib
import os
import sys
from utils.path import resource_path
from loguru_logging import log  # 导入全局日志对象
# 新增：统一的资源定位函数，兼容源码运行与 PyInstaller 打包运行
# 注意：需在任何资源文件（模型、字体等）被引用之前定义


@log.catch
def yolo_colors(cls_id):
    """为每个类别生成唯一的颜色"""
    # 使用固定的颜色列表
    colors = [
        [4, 42, 255],
        [11, 219, 235],
        [243, 243, 243],
        [0, 223, 183],
        [17, 31, 104],
        [255, 111, 221]
    ]
    # 使用类别ID取模获取颜色
    return colors[cls_id % len(colors)]


@log.catch
def compute_iou(b1, b2):
    """计算两个边界框的IoU（交并比）

    Args:
        b1, b2: 边界框坐标 [x1, y1, x2, y2]

    Returns:
        IoU值，范围[0, 1]
    """
    # 计算交集区域坐标
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])

    # 计算交集面积
    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter_area = inter_w * inter_h

    # 计算并集面积
    area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    area2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    union_area = area1 + area2 - inter_area

    # 计算IoU
    return inter_area / union_area if union_area > 0 else 0


@log.catch
def non_max_suppression(boxes, scores, class_ids, iou_threshold=0.5):
    """执行非极大值抑制（NMS）去除重叠的边界框

    Args:
        boxes: 边界框列表，每个边界框格式为 [x1, y1, x2, y2]
        scores: 每个边界框的置信度列表
        class_ids: 每个边界框的类别ID列表
        iou_threshold: IoU阈值，默认为0.5

    Returns:
        经过NMS处理后的边界框、置信度和类别ID
    """
    if not boxes:
        return [], [], []

    # 转换为numpy数组便于处理
    boxes_arr = np.array(boxes)
    scores_arr = np.array(scores)

    # 按置信度从高到低排序
    order = np.argsort(scores_arr)[::-1]

    # 保留的边界框索引
    keep_idx = []

    while order.size > 0:
        # 保留置信度最高的边界框
        i = order[0]
        keep_idx.append(i)

        # 计算当前边界框与其他边界框的IoU
        ious = np.array([compute_iou(boxes_arr[i], boxes_arr[j])
                        for j in order[1:]])

        # 保留IoU小于阈值的边界框
        indices = np.where(ious < iou_threshold)[0]
        order = order[indices + 1]

    # 返回保留的边界框、置信度和类别ID
    return boxes_arr[keep_idx].tolist(), [scores[i] for i in keep_idx], [class_ids[i] for i in keep_idx]


@log.catch
def getInter(box1, box2):
    """计算两个边界框的交集区域"""
    box1_x1, box1_y1, box1_x2, box1_y2 = box1[0] - box1[2] / 2, box1[1] - box1[3] / 2, \
        box1[0] + box1[2] / 2, box1[1] + box1[3] / 2
    box2_x1, box2_y1, box2_x2, box2_y2 = box2[0] - box2[2] / 2, box2[1] - box2[3] / 2, \
        box2[0] + box2[2] / 2, box2[1] + box2[3] / 2

    if box1_x1 > box2_x2 or box1_x2 < box2_x1:
        return 0
    if box1_y1 > box2_y2 or box1_y2 < box2_y1:
        return 0

    x_list = [box1_x1, box1_x2, box2_x1, box2_x2]
    x_list = np.sort(x_list)
    x_inter = x_list[2] - x_list[1]

    y_list = [box1_y1, box1_y2, box2_y1, box2_y2]
    y_list = np.sort(y_list)
    y_inter = y_list[2] - y_list[1]

    inter = x_inter * y_inter
    return inter


@log.catch
def getIou(box1, box2, inter_area):
    """计算两个边界框的IoU"""
    box1_area = box1[2] * box1[3]
    box2_area = box2[2] * box2[3]
    union = box1_area + box2_area - inter_area
    iou = inter_area / union
    return iou


@log.catch
def nms(pred, conf_thres, iou_thres):
    """非极大值抑制（参照inference_onnx.py）"""
    # 过滤低置信度框
    conf = pred[..., 4] > conf_thres
    box = pred[conf == True]

    if len(box) == 0:
        return []

    cls_conf = box[..., 5:]
    cls = []
    for i in range(len(cls_conf)):
        cls.append(int(np.argmax(cls_conf[i])))

    total_cls = list(set(cls))
    output_box = []

    for i in range(len(total_cls)):
        clss = total_cls[i]
        cls_box = []

        for j in range(len(cls)):
            if cls[j] == clss:
                box[j][5] = clss
                cls_box.append(box[j][:6])

        cls_box = np.array(cls_box)
        if len(cls_box) == 0:
            continue

        # 按置信度排序
        box_conf = cls_box[..., 4]
        box_conf_sort = np.argsort(box_conf)[::-1]
        cls_box = cls_box[box_conf_sort]

        while len(cls_box) > 0:
            # 保留置信度最高的框
            max_conf_box = cls_box[0]
            output_box.append(max_conf_box)

            # 删除已保留的框
            cls_box = np.delete(cls_box, 0, 0)

            # 计算与其他框的IoU
            if len(cls_box) == 0:
                break

            del_index = []
            for j in range(len(cls_box)):
                current_box = cls_box[j]
                interArea = getInter(max_conf_box, current_box)
                iou = getIou(max_conf_box, current_box, interArea)
                if iou > iou_thres:
                    del_index.append(j)

            # 删除IoU大于阈值的框
            if del_index:
                cls_box = np.delete(cls_box, del_index, 0)

    return output_box


@log.catch
def ai_detect(image_paths):
    # image_paths=[
    #     "D:\\image\\2222\\20251121_44\\112632_IR.jpg",
    #     "D:\\image\2222\20251120_42\\181557_color.jpg"
    # ]
    # 解析命令行参数获取模型路径
    model_path = resource_path('ai/best.onnx')
    try:
        # 创建ONNX推理会话
        providers = ['CPUExecutionProvider']
        # 尝试使用GPU
        try:
            if ort.get_device() == 'GPU':
                providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        except:
            pass
        model = ort.InferenceSession(model_path, providers=providers)
        # 获取模型输入名称
        model_input_name = model.get_inputs()[0].name
        log.info(f"成功加载ONNX模型: {model_input_name} 路径:{model_path}")
    except Exception as e:
        log.error(f"ONNX模型加载失败: {e}")
        return None
    # 定义类别名称映射（根据实际模型类别）
    id2name = {0: '异常黑点', 1: '异常视盘', 2: '异常黄斑'}  # 请根据实际模型类别调整
    font_path = resource_path('ai/Arial.Unicode.ttf')
    ImageFont.truetype(font_path, 48)

    # 聚合用于叠加到彩图上的检测结果
    aggregated_boxes: list[np.ndarray] = []
    aggregated_cls_ids: list[int] = []
    aggregated_scores: list[float] = []
    color_img_path = None
    color_img_idx = None
    for idx, img_info in enumerate(image_paths):
        if img_info["detect_file_name"].endswith("_color.jpg"):
            log.debug(f"当前图片为彩图:{img_info}")
            color_img_idx = idx
            continue
        path = str(pathlib.Path(img_info['detect_file_path']).joinpath(
            img_info['detect_file_name']))
        log.debug(f"当前处理图片路径:{path}")
        try:
            img = cv2.imread(path)
            # 图像预处理（参照inference_onnx.py）
            input_height, input_width = 640, 640  # 固定输入尺寸
            img0 = img.copy()

            # 计算缩放比例
            x_scale = img0.shape[1] / input_width
            y_scale = img0.shape[0] / input_height

            # 图像预处理
            img_resized = cv2.resize(img, (input_width, input_height))
            img_resized = img_resized / 255.0  # 归一化到[0,1]
            img_resized = np.transpose(img_resized, (2, 0, 1))  # HWC -> CHW
            img_resized = np.expand_dims(img_resized, axis=0)  # 添加batch维度

            # 执行推理
            outputs = model.run(None, {model_input_name: img_resized.astype(np.float32)})
            # 处理输出结果（参照inference_onnx.py）
            pred = outputs[0]
            pred = np.squeeze(pred)
            pred = np.transpose(pred, (1, 0))

            # 提取置信度和类别
            pred_class = pred[..., 4:]
            pred_conf = np.max(pred_class, axis=-1)
            pred = np.insert(pred, 4, pred_conf, axis=-1)

            # 执行NMS
            result = nms(pred, 0.25, 0.7)  # 使用inference_onnx.py中的nms函数参数

            # 解析检测结果
            boxes = []
            class_ids = []
            scores = []
            log.debug(f"result={result}")
            for detect in result:
                # 转换坐标：中心点+宽高 -> 左上角+右下角，并映射回原始图像尺寸
                cx, cy, w, h, conf, cls_id = detect
                x1 = int((cx - w/2) * x_scale)
                y1 = int((cy - h/2) * y_scale)
                x2 = int((cx + w/2) * x_scale)
                y2 = int((cy + h/2) * y_scale)

                # 确保坐标在图像范围内
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(img.shape[1] - 1, x2)
                y2 = min(img.shape[0] - 1, y2)

                boxes.append([x1, y1, x2, y2])
                class_ids.append(int(cls_id))
                scores.append(float(conf))
            log.debug(
                f"detect_file_name={img_info['detect_file_name']}  boxes={boxes}")
            # OpenCV 画框
            for box, cls_id in zip(boxes, class_ids):
                x1, y1, x2, y2 = map(int, box)
                color = yolo_colors(cls_id)
                cv2.rectangle(img, (x1, y1), (x2, y2),
                              (color[2], color[1], color[0]), 5)

            # PIL 画中文标签
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ImageDraw.Draw(img_pil)

            for box, cls_id, score in zip(boxes, class_ids, scores):
                x1, y1, x2, y2 = map(int, box)
                color = yolo_colors(cls_id)

            source_file = pathlib.Path(path)
            save_dir = source_file.parent
            save_name = source_file.name.replace(".jpg", "_detected.jpg")
            save_path = save_dir.joinpath(save_name)
            cv2.imwrite(str(save_path), cv2.cvtColor(
                np.array(img_pil), cv2.COLOR_RGB2BGR))

            # 收集标签与颜色
            label_map = {}
            for cid in set(class_ids):
                cname = id2name[cid]
                color = yolo_colors(cid)
                label_map[cname] = '#{:02X}{:02X}{:02X}'.format(*color)
            image_paths[idx]['detected'] = {
                "file_path": save_path.parent,
                "file_name": save_path.name,
                "labels": label_map,
                "is_primary": False
            }
            # 聚合框，用于稍后叠加到彩图
            aggregated_boxes.extend(boxes)
            aggregated_cls_ids.extend(class_ids)
            aggregated_scores.extend(scores)

        except Exception as e:
            log.error(f"处理灰度图 {path} 时出错: {e}")
            return None

    # -------------------- 聚合结果去重（NMS） --------------------
    if aggregated_boxes:
        # 使用已定义的NMS函数处理聚合的检测结果
        aggregated_boxes, aggregated_scores, aggregated_cls_ids = non_max_suppression(
            aggregated_boxes, aggregated_scores, aggregated_cls_ids, iou_threshold=0.5
        )

    # -------------------- 叠加到彩色图 --------------------
    if color_img_idx is None:
        log.debug(f"无彩图 image_paths={image_paths}")
        return {
            "imgs": image_paths
        }
    color_img_path = str(pathlib.Path(image_paths[color_img_idx]['detect_file_path']).joinpath(
        image_paths[color_img_idx]['detect_file_name']))
    img_color = cv2.imread(color_img_path)
    # 画框
    for box, cls_id, score in zip(aggregated_boxes, aggregated_cls_ids, aggregated_scores):
        x1, y1, x2, y2 = map(int, box)
        color = yolo_colors(cls_id)
        cv2.rectangle(img_color, (x1, y1), (x2, y2),
                      (color[2], color[1], color[0]), 5)

    # 画中文标签
    if aggregated_boxes:
        log.debug(
            f"彩色图 detect_file_name={image_paths[color_img_idx]['detect_file_name']}  boxes={aggregated_boxes}")
        img_pil = Image.fromarray(cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(img_pil)

        for box, cls_id, score in zip(aggregated_boxes, aggregated_cls_ids, aggregated_scores):
            x1, y1, x2, y2 = map(int, box)
            color = yolo_colors(int(cls_id))

        img_color = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    color_source_path = pathlib.Path(color_img_path)
    color_save_dir = color_source_path.parent
    color_save_name = color_source_path.name.replace(".jpg", "_detected.jpg")
    color_save_path = color_save_dir.joinpath(color_save_name)
    cv2.imwrite(str(color_save_path), img_color)

    # 彩图的标签为聚合后的标签
    c_label_map = {}
    for acid in set(aggregated_cls_ids):
        cname = id2name[acid]
        color = yolo_colors(acid)
        c_label_map[cname] = '#{:02X}{:02X}{:02X}'.format(*color)
    image_paths[color_img_idx]['detected'] = {
        "file_path": color_save_path.parent,
        "file_name": color_save_path.name,
        "labels": c_label_map,
        "is_primary": True
    }
    log.debug(f"image_paths={image_paths}")
    return {
        "imgs": image_paths
    }


if __name__ == "__main__":
    image_paths = [
        {
            "image_id": 1,
            "detect_file_path": "/Users/stunum/Downloads/阅片/Ai_results/00906241金浩/",
            "detect_file_name": "test_1_color.jpg"
        },
        {
            "image_id": 2,
            "detect_file_path": "/Users/stunum/Downloads/阅片/Ai_results/00906241金浩/",
            "detect_file_name": "test_1_g.jpg"
        },
        {
            "image_id": 3,
            "detect_file_path": "/Users/stunum/Downloads/阅片/Ai_results/00906241金浩/",
            "detect_file_name": "test_1_R.jpg"
        }
    ]
    ai_detect(image_paths)
